"""Install the local Codex skills in the current user's skill directory."""

import os
from pathlib import Path
import stat
import subprocess


SKILLS = ("qa-onboard-repo", "jira-test-generator")


def is_link(path: Path) -> bool:
    if path.is_symlink():
        return True
    if os.name != "nt":
        return False
    try:
        return bool(path.lstat().st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT)
    except FileNotFoundError:
        return False


def managed_skill_target(path: Path, skill: str) -> bool:
    parts = path.resolve(strict=False).parts
    return len(parts) >= 4 and parts[-4:] == ("agent-adapters", "codex", "skills", skill)


def create_directory_link(source: Path, destination: Path) -> None:
    try:
        destination.symlink_to(source, target_is_directory=True)
    except OSError:
        if os.name != "nt":
            raise
        quote = lambda path: "'" + str(path).replace("'", "''") + "'"
        command = f"New-Item -ItemType Junction -Path {quote(destination)} -Target {quote(source)} | Out-Null"
        result = subprocess.run(
            ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", command],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode:
            raise OSError(result.stderr.strip() or "Could not create a skill link")


def remove_link(path: Path) -> None:
    if path.is_symlink():
        path.unlink()
    elif os.name == "nt" and is_link(path):
        os.rmdir(path)
    else:
        raise OSError(f"Refusing to remove a non-link path: {path}")


def install_skills(project_root: Path, skills_root: Path) -> list[tuple[Path, Path]]:
    project_root = project_root.resolve(strict=True)
    source_root = project_root / "skills"
    links = [(source_root / name, skills_root / name) for name in SKILLS]
    for source, destination in links:
        if not (source / "SKILL.md").is_file():
            raise FileNotFoundError(f"Missing skill source: {source}")
        occupied = destination.exists() or is_link(destination)
        if occupied and destination.resolve(strict=False) != source.resolve():
            if not managed_skill_target(destination, source.name):
                raise FileExistsError(f"Refusing to replace existing skill path: {destination}")

    skills_root.mkdir(parents=True, exist_ok=True)
    for source, destination in links:
        if destination.resolve(strict=False) == source.resolve():
            continue
        if destination.exists() or is_link(destination):
            remove_link(destination)
        create_directory_link(source, destination)

    return links


def main() -> int:
    project_root = Path(__file__).resolve().parents[1]
    skills_root = Path.home() / ".agents" / "skills"
    try:
        for source, destination in install_skills(project_root, skills_root):
            print(f"Linked {destination} -> {source}")
        return 0
    except (OSError, ValueError) as error:
        print(f"Skill installation failed: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
