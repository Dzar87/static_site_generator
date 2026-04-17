import logging
from pathlib import Path
import shutil

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


def main() -> int:
    LOG.info("Starting...")
    src = Path(__file__).parent.parent / "static"
    LOG.info("Static source: %s", src)
    dst = Path(__file__).parent.parent / "public"
    LOG.info("Static destination: %s", dst)
    sync_static(src, dst)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
