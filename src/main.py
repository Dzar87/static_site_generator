import logging
from pathlib import Path
import shutil

from template import Template
from textnode import parse_markdown_file

logging.basicConfig(level=logging.DEBUG)
LOG = logging.getLogger(__name__)


def _copy_static(src: Path, dst: Path) -> None:
    for f in src.iterdir():
        LOG.debug("Processing: %s", f.name)
        if f.is_dir():
            new_dst = dst / f.name
            LOG.debug("Creating directory: %s in %s", new_dst.name, dst.name)
            new_dst.mkdir()
            _copy_static(f, new_dst)
        else:
            LOG.debug("Copying file: %s -> %s", f.name, dst.name)
            shutil.copy(f, dst / f.name)


def sync_static(src: Path, dst: Path) -> None:
    dst = dst.resolve()
    if dst.exists() and not dst.is_dir():
        raise ValueError(f"'{dst}' is not a directory")
    src = src.resolve(strict=True)
    if not src.is_dir():
        raise ValueError(f"'{src}' is not a directory.")
    LOG.debug("Unlinking: %s", dst)
    if dst.exists():
        shutil.rmtree(dst)
    dst.mkdir(mode=0o755, parents=False, exist_ok=False)
    _copy_static(src, dst)


def generate_page(src: Path, dst: Path, tmpl: Path) -> None:
    LOG.info(
        "Generating page from %s to %s using %s", src.name, dst.name, tmpl.name
    )
    template = Template(tmpl)
    template.validate()
    title, content = parse_markdown_file(src)
    template.render_to_file(dst, context={"title": title, "content": content})


def main() -> int:
    LOG.info("Starting...")
    # TODO: Make these configurable
    root_path = Path(__file__).parent.parent
    static_dir = root_path / "static"
    dst = root_path / "public"
    content_dir = root_path / "content"
    tmpl_dir = root_path / "templates"

    LOG.info("Static dir: %s", static_dir)
    LOG.info("Destination dir: %s", dst)
    LOG.info("Content dir: %s", content_dir)
    LOG.info("Template dir: %s", tmpl_dir)

    try:
        sync_static(static_dir, dst)
    except (ValueError, FileNotFoundError):
        LOG.exception("Failed to sync static")
        return 1

    content_path = content_dir / "index.md"
    tmpl_path = tmpl_dir / "index.html"

    try:
        generate_page(content_path, dst / "index.html", tmpl_path)
    except (ValueError, AssertionError, FileNotFoundError):
        LOG.exception("Failed to generate page")
        return 1

    LOG.info("Finished.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
