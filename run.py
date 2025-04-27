import asyncio
import logging
import os
import pathlib
import shutil

import aiohttp
import aiohttp.abc
import aiohttp.web
import jinja2
import markdown
import toml
import user_agents
import watchfiles

# Configuration.
ROOT_DIR = pathlib.Path(__file__).parent
CONTENT_DIR = ROOT_DIR / "content"
OUTPUT_DIR = ROOT_DIR / "output"
TEMPLATE_DATA_FILENAME = "_config.toml"
HOST = "localhost"
PORT = 8000


# Logging.
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(message)s")
logging.getLogger("watchfiles.main").setLevel(
    logging.WARNING
)  # Stop watchfiles from logging file changes, as we do it instead.


def is_working_filename(filename):
    # A working file has a name which starts with either an underscore or a dot.
    return pathlib.Path(filename).name[0] in ("_", ".")


def is_template_filename(filename):
    # A template filename is a non-working filename with a .html extension.
    p = pathlib.Path(filename)
    return p.suffix == ".html" and not is_working_filename(p)


def rpr(filename):
    """Return the Relative Path to Root. For tidier logging."""
    return pathlib.Path(filename).relative_to(ROOT_DIR)


def create_fresh_output_directory():
    logger.info(f"Using content in: {CONTENT_DIR} ({rpr(CONTENT_DIR)})")
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    shutil.copytree(CONTENT_DIR, OUTPUT_DIR)
    logger.info(
        f"Cloned content into fresh output directory: {OUTPUT_DIR} ({rpr(OUTPUT_DIR)})"
    )


def render_markdown():
    md = markdown.Markdown()
    for root, dirs, files in OUTPUT_DIR.walk():
        for name in files:
            if name.endswith(".md"):
                md_filename = root / name
                html_filename = md_filename.with_suffix(".html")
                md.convertFile(
                    input=str(md_filename),
                    output=str(html_filename),
                )
                md_filename.unlink()
                logger.info(f"Rendered markdown in: {rpr(md_filename)}")


def render_templates():
    data = toml.load(OUTPUT_DIR / TEMPLATE_DATA_FILENAME)
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(OUTPUT_DIR),
        extensions=["jinja2_workarounds.MultiLineInclude"],
    )
    template_filenames = env.list_templates(filter_func=is_template_filename)
    for template_filename in template_filenames:
        template = env.get_template(template_filename)
        p = OUTPUT_DIR / template_filename
        with open(p, "w") as f:
            f.write(template.render(data))
        logger.info(f"Rendered template: {rpr(p)}")


def remove_working_files():
    n_files = 0
    n_dirs = 0
    for root, dirs, files in OUTPUT_DIR.walk(top_down=False):
        for name in files:
            p = root / name
            if is_working_filename(p):
                n_files += 1
                logger.debug(f"Removing working file: {rpr(p)}")
                p.unlink()
        for name in dirs:
            p = root / name
            if len(list(p.iterdir())) == 0:
                n_dirs += 1
                logger.debug(f"Removing empty directory: {rpr(p)}")
                os.rmdir(p)
    logger.info(
        f"Removed {n_files} working files and {n_dirs} empty directories from output directory"
    )


def create_xml_sitemap():
    pass
    # logger.info("Creating XML sitemap")
    # sitemap = Sitemap()
    # for (root, dirs, files) in OUTPUT_DIR.walk(top_down=False):
    #     for name in files:
    #         p = root / name
    #         if is_working_filename(p):
    #             continue
    #         if p.suffix == ".html":
    #             sitemap.add(p.relative_to(OUTPUT_DIR).as_posix())
    # with open(OUTPUT_DIR / "sitemap.xml", "w") as f:
    #     f.write(sitemap.to_string())
    # logger.info("Created XML sitemap")


def rebuild():
    create_fresh_output_directory()
    render_markdown()
    render_templates()
    remove_working_files()
    create_xml_sitemap()
    logger.info(f"Rebuilt all files in: {rpr(OUTPUT_DIR)}")


class AccessLogger(aiohttp.abc.AbstractAccessLogger):
    # Use a hand-crafted httpio access logger to fully control the detail.
    # In particular, to unpack the User-Agent string.

    def log(self, request, response, time):
        ua = user_agents.parse(request.headers["User-Agent"])
        browser = ua.browser.family
        version = ua.browser.version_string
        if version:
            browser += "-" + version
        device = ua.device.family
        self.logger.info(
            f"Completed request from client {browser} on {device}: {request.path}"
        )


async def get_changes():
    async for changes in watchfiles.awatch(CONTENT_DIR):
        for change, filename in list(changes):
            if change == watchfiles.Change.added:
                logger.info(f"Noticed new file added: {rpr(filename)}")
            elif change == watchfiles.Change.deleted:
                logger.info(f"Noticed existing file deleted: {rpr(filename)}")
            elif change == watchfiles.Change.modified:
                logger.info(f"Noticed existing file modified: {rpr(filename)}")
        yield changes


async def run_server_and_rebuild_after_changes():
    web_sockets = set()  # TODO move to app["web_sockets"]

    async def websocket_handler(request):
        ws = aiohttp.web.WebSocketResponse()
        web_sockets.add(ws)
        await ws.prepare(request)
        logger.info("Started new hot reloader websocket")
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
            logger.info("Closed hot reloader websocket")
        finally:
            web_sockets.remove(ws)
        return ws

    async def send_reload_action():
        logger.info(f"Signalling to {len(web_sockets)} hot reloaders")
        for ws in list(web_sockets):
            await ws.send_str("reload")

    app = aiohttp.web.Application()
    app.router.add_static("/", OUTPUT_DIR, show_index=True)
    app.router.add_get("/ws", websocket_handler)
    runner = aiohttp.web.AppRunner(
        app,
        access_log_class=AccessLogger,
        access_log=logger,
        handle_signals=True,
        handler_cancellation=True,
    )
    await runner.setup()
    site = aiohttp.web.TCPSite(runner, host=HOST, port=PORT)
    logger.info(f"Starting local server on http://{HOST}:{PORT}")
    logger.info(f"Serving files from: {rpr(OUTPUT_DIR)}")
    logger.info(f"Watching for changes in: {rpr(CONTENT_DIR)}")
    try:
        await site.start()
        async for _ in get_changes():
            rebuild()
            await send_reload_action()
    finally:
        logger.info("Stopping server")
        await runner.cleanup()


async def main():
    rebuild()
    await run_server_and_rebuild_after_changes()


if __name__ == "__main__":
    asyncio.run(main())
