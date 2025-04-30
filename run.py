import asyncio
import glob
import logging
import os
import pathlib
import shutil

import aiohttp
import aiohttp.abc
import aiohttp.web
import jinja2
import markdown_it
import tidy
import toml
import user_agents
import watchfiles
from mdit_py_plugins.footnote import footnote_plugin as markdown_footnote_plugin

ROOT_DIR = pathlib.Path(__file__).parent


# Configure Logging.
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(message)s")
logging.getLogger("watchfiles.main").setLevel(
    logging.WARNING
)  # Stop watchfiles from logging file changes, as we do it instead.


def log(message, *args):
    # Make all pathlib.Path args relative to ROOT_DIR.
    tmp = [
        str(pathlib.Path(arg).relative_to(ROOT_DIR))
        if isinstance(arg, pathlib.Path)
        else arg
        for arg in args
    ]
    logger.info(message.format(*tmp))


class Builder:
    def __init__(self, content_dir, output_dir):
        self.output_dir = output_dir
        self.content_dir = content_dir

    def _is_working_filename(self, filename):
        # A working file has a name which starts with either an underscore or a dot.
        return pathlib.Path(filename).name[0] in ("_", ".")

    def _is_template_filename(self, filename):
        # A template filename is a non-working filename with a .html extension.
        p = pathlib.Path(filename)
        return p.suffix == ".html" and not self._is_working_filename(p)

    def create_fresh_output_directory(self):
        log(f"Using content in: {self.content_dir} ({{}})", self.content_dir)

        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)
        shutil.copytree(self.content_dir, self.output_dir)
        log(
            f"Cloned content into fresh output directory: {self.output_dir} ({{}})",
            self.output_dir,
        )

    def _add_template_data(self, env):
        for filename in glob.glob(
            "**.toml", root_dir=self.output_dir, recursive=True
        ):
            log("Reading template data from: {}", filename)
            data = toml.load(self.output_dir / filename)
            env.globals.update(data)

    def _add_markdown_filter(self, env):
        @jinja2.pass_context
        def convert_markdown(context, value):
            if value.startswith(".") or "/" not in value:
                # Relative to template file.
                markdown_filename = (
                    self.output_dir / pathlib.Path(context.name).parent / value
                )
            else:
                # Relative to main content root.
                markdown_filename = self.output_dir / value
            md = markdown_it.MarkdownIt(
                "commonmark", {"typographer": True, "linkify": True}
            )
            md.use(markdown_footnote_plugin)
            md.enable(["replacements", "smartquotes", "linkify", "table"])
            log("Converted markdown from: {}", markdown_filename)
            with open(markdown_filename, "r") as f:
                return md.render(f.read())

        env.filters["markdown"] = convert_markdown

    def render_templates(self):
        loader = jinja2.FileSystemLoader(self.output_dir)
        env = jinja2.Environment(loader=loader)
        self._add_template_data(env)
        self._add_markdown_filter(env)
        template_filenames = env.list_templates(
            filter_func=self._is_template_filename
        )
        for template_filename in template_filenames:
            template = env.get_template(template_filename)
            p = self.output_dir / template_filename
            with open(p, "w") as f:
                f.write(template.render())
            log("Rendered template: {}", p)

    def remove_working_files(self):
        n_files = 0
        n_dirs = 0
        for root, dirs, files in self.output_dir.walk(top_down=False):
            for name in files:
                p = root / name
                if self._is_working_filename(p):
                    n_files += 1
                    p.unlink()
            for name in dirs:
                p = root / name
                if len(list(p.iterdir())) == 0:
                    n_dirs += 1
                    os.rmdir(p)
        log(
            f"Removed {n_files} working files and {n_dirs} empty directories from output directory"
        )

    def tidy_html_files(self):
        for root, dirs, files in self.output_dir.walk():
            for name in files:
                p = root / name
                if p.suffix == ".html":
                    doc = tidy.parse(
                        str(p),
                        indent="yes",
                        wrap=120,
                        drop_empty_elements="no",
                        wrap_sections="no",
                    )
                    errors = doc.get_errors()
                    if errors:
                        for e in errors:
                            log(f"Html-tidy found problem in {{}}: {e}", p)
                        output_filename = p.with_suffix(".tidy.html")
                        log(
                            "Not updating file, but see tidy version in {}",
                            output_filename,
                        )
                    else:
                        output_filename = p
                        log("Html-tidy ok: {}", p)
                    with open(output_filename, "w") as fp:
                        fp.write(doc.gettext())

    def create_xml_sitemap(self):
        log("Created XML sitemap - TODO!!")
        # sitemap = Sitemap()
        # for (root, dirs, files) in OUTPUT_DIR.walk(top_down=False):
        #     for name in files:
        #         p = root / name
        #         if _is_working_filename(p):
        #             continue
        #         if p.suffix == ".html":
        #             sitemap.add(p.relative_to(OUTPUT_DIR).as_posix())
        # with open(OUTPUT_DIR / "sitemap.xml", "w") as f:
        #     f.write(sitemap.to_string())
        # log("Created XML sitemap")

    def rebuild(self):
        self.create_fresh_output_directory()
        self.render_templates()
        self.remove_working_files()
        self.tidy_html_files()
        self.create_xml_sitemap()
        log("Rebuilt all files in: {}", self.output_dir)


class _ServerAccessLogger(aiohttp.abc.AbstractAccessLogger):
    # Use a hand-crafted httpio access logger to fully control the detail.
    # In particular, to unpack the User-Agent string.

    def log(self, request, response, time):
        ua = user_agents.parse(request.headers["User-Agent"])
        browser = ua.browser.family
        version = ua.browser.version_string
        if version:
            browser += "-" + version
        device = ua.device.family
        log(
            f"Completed request from client {browser} on {device}: {request.path}"
        )


class Server:
    host = "localhost"
    port = 8000

    def __init__(self, directory):
        self.directory = directory
        self.web_sockets = set()

    async def signal_hot_reloaders(self):
        log(f"Signalling to {len(self.web_sockets)} hot reloaders")
        for ws in list(self.web_sockets):
            await ws.send_str("reload")

    async def _close_hot_reloaders(self):
        log(f"Closing {len(self.web_sockets)} hot reloaders")
        for ws in list(self.web_sockets):
            await ws.close()

    async def start(self):
        async def websocket_handler(request):
            ws = aiohttp.web.WebSocketResponse()
            self.web_sockets.add(ws)
            await ws.prepare(request)
            log("Started new hot reloader websocket")
            try:
                async for msg in ws:
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        if msg.data == "close":
                            await ws.close()
                    elif msg.type == aiohttp.WSMsgType.ERROR:
                        print(
                            "ws connection closed with exception %s"
                            % ws.exception()
                        )
                log("Closed hot reloader websocket")
            finally:
                self.web_sockets.remove(ws)
            return ws

        app = aiohttp.web.Application()
        app.router.add_static("/", self.directory, show_index=True)
        app.router.add_get("/ws", websocket_handler)
        self._runner = aiohttp.web.AppRunner(
            app,
            access_log_class=_ServerAccessLogger,
            access_log=logger,
            handle_signals=False,
            handler_cancellation=True,
        )
        await self._runner.setup()
        site = aiohttp.web.TCPSite(self._runner, self.host, self.port)
        log(f"Starting local server on http://{self.host}:{self.port}")
        log("Serving files from: {}", self.directory)
        await site.start()

    async def stop(self):
        log("Stopping server")
        await self._close_hot_reloaders()
        await self._runner.cleanup()


class Watcher:
    def __init__(self, directory):
        self.directory = directory
        self._change_event = asyncio.Event()

    async def _start(self):
        log("Watching for changes in: {}", self.directory)
        async for changes in watchfiles.awatch(self.directory):
            for change, filename in list(changes):
                if change == watchfiles.Change.added:
                    log("Noticed file added: {}", filename)
                elif change == watchfiles.Change.deleted:
                    log("Noticed file deleted: {}", filename)
                elif change == watchfiles.Change.modified:
                    log("Noticed file modified: {}", filename)
            self._change_event.set()

    async def start(self):
        return asyncio.create_task(self._start())

    async def wait_for_change(self):
        await self._change_event.wait()
        self._change_event.clear()


async def main():
    content_dir = ROOT_DIR / "content"
    output_dir = ROOT_DIR / "output"

    builder = Builder(content_dir, output_dir)
    watcher = Watcher(content_dir)
    server = Server(output_dir)

    await watcher.start()
    await server.start()
    try:
        while True:
            builder.rebuild()
            await server.signal_hot_reloaders()
            await watcher.wait_for_change()
    except asyncio.CancelledError:
        # asyncio raises CancelledError on ctrl-c signal.
        # See https://docs.python.org/3/library/asyncio-runner.html#handling-keyboard-interruption
        # We take responsibility for cleanup and swallow the exception.
        await server.stop()
        log("Bye")


if __name__ == "__main__":
    asyncio.run(main())
