"""Stage a skills-only plugin without private checkout profiles or settings."""

from pathlib import Path
import shutil
import sys


PACKAGE_FILES = ("plugin.json", "scripts/qa_agent.py")
PACKAGE_DIRECTORIES = ("skills", "schemas", "repo-profiles/template")


def package_plugin(source_root: Path, output_root: Path) -> Path:
    source_root = source_root.resolve(strict=True)
    output_root = output_root.resolve()
    for name in PACKAGE_FILES:
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
        for name in PACKAGE_DIRECTORIES:
            shutil.copytree(
                source_root / name, destination / name,
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store"),
            )
    except OSError:
        shutil.rmtree(destination)
        raise
    return destination


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    try:
        print(package_plugin(root, root / "dist"))
        return 0
    except (OSError, ValueError) as error:
        print(f"Plugin packaging failed: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
