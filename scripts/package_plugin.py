"""Package a Git-distributable plugin without private profiles or settings."""

import argparse
import json
from pathlib import Path
import re
import shutil
import sys
import zipfile


PACKAGE_FILES = (
    "plugin.json", ".claude-plugin/plugin.json", "scripts/qa_agent.py", "requirements-core.txt",
    "LICENSE", "assets/icon.svg",
)
PACKAGE_FILE_MAPPINGS = {"docs/plugin-readme.md": "README.md"}
PACKAGE_DIRECTORIES = ("skills", "schemas", "repo-profiles/template")


def package_plugin(source_root: Path, output_root: Path) -> Path:
    source_root = source_root.resolve(strict=True)
    output_root = output_root.resolve()
    for name in (*PACKAGE_FILES, *PACKAGE_FILE_MAPPINGS):
        if not (source_root / name).is_file():
            raise FileNotFoundError(f"Missing package file: {name}")
    for name in PACKAGE_DIRECTORIES:
        directory = source_root / name
        if not directory.is_dir():
            raise FileNotFoundError(f"Missing package directory: {name}")
        if output_root == directory or directory in output_root.parents:
            raise ValueError(f"Output must be outside bundled directory: {directory}")

    destination = output_root / "universal-qa-agent"
    destination.mkdir(parents=True, exist_ok=False)
    try:
        for name in PACKAGE_FILES:
            target = destination / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_root / name, target)
        for source, target in PACKAGE_FILE_MAPPINGS.items():
            shutil.copy2(source_root / source, destination / target)
        for name in PACKAGE_DIRECTORIES:
            shutil.copytree(
                source_root / name, destination / name,
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store"),
            )
    except OSError:
        shutil.rmtree(destination)
        raise
    return destination


def archive_plugin(package_root: Path, output_root: Path) -> Path:
    manifest = json.loads((package_root / "plugin.json").read_text(encoding="utf-8"))
    version = manifest["version"]
    if not isinstance(version, str) or not re.fullmatch(
        r"[0-9]+\.[0-9]+\.[0-9]+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?", version,
    ):
        raise ValueError("Plugin version must be a safe semantic version")
    output_root.mkdir(parents=True, exist_ok=True)
    archive = output_root / f"universal-qa-agent-{version}.zip"
    with zipfile.ZipFile(archive, "x", compression=zipfile.ZIP_DEFLATED) as bundle:
        try:
            for path in sorted(package_root.rglob("*")):
                if path.is_symlink():
                    raise ValueError(f"Plugin archive cannot contain symlinks: {path}")
                if path.is_file():
                    bundle.write(path, path.relative_to(package_root).as_posix())
        except (OSError, ValueError):
            bundle.close()
            archive.unlink()
            raise
    return archive


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", action="store_true", help="also create a versioned submission ZIP in dist/")
    args = parser.parse_args(argv)
    root = Path(__file__).resolve().parents[1]
    try:
        package = package_plugin(root, root / "plugins")
        print(package)
        if args.archive:
            print(archive_plugin(package, root / "dist"))
        return 0
    except (OSError, ValueError) as error:
        print(f"Plugin packaging failed: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
