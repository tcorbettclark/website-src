import asyncio
import logging
import os
import shutil

import jinja2
import toml
import watchfiles
from aiohttp import web

# Configure logging.
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(message)s")
logging.getLogger("watchfiles.main").setLevel(
    logging.WARNING
)  # Stop watchfiles from logging file changes, as we do it instead.

# Basic configuration.
CONTENT_DIR = os.path.join(os.path.dirname(__file__), "content")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
TEMPLATE_DATA_FILENAME = "_template_data.toml"
HOST = "localhost"
PORT = 8000


def is_source_filename(name):
    return any(
        x.startswith("_") or x.startswith(".") for x in os.path.split(name)
    )


def is_template_filename(name):
    return name.endswith(".html") and not is_source_filename(name)


def render_markdown():
    # read frontmatter (TOML)
    # TODO also delete the .md file onces processed.
    # log what it's doing, including applying template.
    pass


def render_templates():
    data = toml.load(os.path.join(OUTPUT_DIR, TEMPLATE_DATA_FILENAME))
    loader = jinja2.FileSystemLoader(OUTPUT_DIR)
    env = jinja2.Environment(loader=loader)
    template_filenames = env.list_templates(filter_func=is_template_filename)
    for template_filename in template_filenames:
        full_name = os.path.join(OUTPUT_DIR, template_filename)
        logger.info(f"Rendering template {full_name}")
        template = env.get_template(template_filename)
        with open(full_name, "w") as f:
            f.write(template.render(data))


def remove_source_files():
    n_files = 0
    n_dirs = 0
    for root, dirs, files in os.walk(OUTPUT_DIR, topdown=False):
        for file in files:
            full_name = os.path.join(root, file)
            if is_source_filename(full_name):
                n_files += 1
                logger.debug(f"Removing source file {full_name}")
                os.remove(full_name)
        for dir in dirs:
            full_name = os.path.join(root, dir)
            if is_source_filename(full_name):
                n_dirs += 1
                logger.debug(f"Removing source directory {full_name}")
                shutil.rmtree(full_name)
            else:
                full_name = os.path.join(root, dir)
                if len(os.listdir(full_name)) == 0:
                    n_dirs += 1
                    logger.debug(f"Removing empty directory {full_name}")
                    os.rmdir(full_name)
    logger.info(
        f"Removed {n_files} source files and {n_dirs} source directories from output directory"
    )


def rebuild():
    logger.info(f"Creating fresh output directory {OUTPUT_DIR}")
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    shutil.copytree(CONTENT_DIR, OUTPUT_DIR)
    render_markdown()
    render_templates()
    remove_source_files()


async def run_server_and_rebuild_after_changes():
    app = web.Application()
    app.router.add_static("/", path=OUTPUT_DIR, show_index=True)

    runner = web.AppRunner(
        app,
        access_log=logger,
        access_log_format="Web request HTTP %r %s %b",
        handle_signals=True,
    )
    await runner.setup()
    site = web.TCPSite(runner, host=HOST, port=PORT)
    logger.info(f"Starting test server on http://{HOST}:{PORT}")
    logger.info(f"Serving files from {OUTPUT_DIR}")
    logger.info(f"Watching for changes in {CONTENT_DIR}")
    try:
        await site.start()
        async for changes in watchfiles.awatch(CONTENT_DIR):
            for change, filename in list(changes):
                if change == watchfiles.Change.added:
                    logger.info(f"Noticed new file added: {filename}")
                elif change == watchfiles.Change.deleted:
                    logger.info(f"Noticed existing file deleted: {filename}")
                elif change == watchfiles.Change.modified:
                    logger.info(f"Noticed existing file modified: {filename}")
            rebuild()
            logger.info(
                f"Continuing to serve (updated) files from {OUTPUT_DIR}"
            )
    finally:
        logger.info("Stopping server")
        await runner.cleanup()


async def main():
    logger.info(f"Using content directory {CONTENT_DIR}")
    rebuild()
    await run_server_and_rebuild_after_changes()


if __name__ == "__main__":
    asyncio.run(main())
