"""Link the shared workflows into supported coding agents' user skill directories."""

from pathlib import Path

from install_codex_skills import (
    SKILLS,
    install_skills as install_skill_root,
    is_link,
)


HOST_SKILLS_DIRS = {
    "Claude Code": Path(".claude/skills"),
    "GitHub Copilot": Path(".copilot/skills"),
}


def install_skills(project_root: Path, home: Path) -> list[tuple[str, Path, Path]]:
    project_root = project_root.resolve(strict=True)
    source_root = project_root / "skills"
    links = [(host, source_root / name, home / skills_dir / name) for host, skills_dir in HOST_SKILLS_DIRS.items() for name in SKILLS]

    for _, source, destination in links:
        if not (source / "SKILL.md").is_file():
            raise FileNotFoundError(f"Missing skill source: {source}")
        occupied = destination.exists() or is_link(destination)
        if occupied and destination.resolve(strict=False) != source.resolve():
            raise FileExistsError(f"Refusing to replace existing skill path: {destination}")

    for skills_dir in HOST_SKILLS_DIRS.values():
        install_skill_root(project_root, home / skills_dir)
    return links


def main() -> int:
    project_root = Path(__file__).resolve().parents[1]
    try:
        for host, source, destination in install_skills(project_root, Path.home()):
            print(f"{host}: linked {destination} -> {source}")
        return 0
    except (OSError, ValueError) as error:
        print(f"Skill installation failed: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
