#!/usr/bin/env python3
"""Discover and print persistent Universal QA Agent repository knowledge."""

import argparse
import os
from pathlib import Path
import sys


KNOWLEDGE_FILES = ("profile.yaml", "conventions.md", "patterns.md")
APPROVAL_MARKER = ".profile-approved"


def absolute_directory(value: str) -> Path:
    path = Path(value).expanduser()
    if not path.is_absolute():
        raise ValueError("Profile storage must be an absolute path.")
    return path.resolve()


def profiles_root() -> Path:
    override = os.environ.get("UQA_PROFILES_DIR")
    if override:
        return absolute_directory(override)
    return Path.home() / ".local" / "share" / "universal-qa-agent" / "repo-profiles"


def available_profiles(root: Path | None = None) -> list[Path]:
    root = root if root is not None else profiles_root()
    if not root.exists():
        return []
    return sorted(
        path for path in root.iterdir()
        if path.is_dir() and (path / "profile.yaml").is_file()
        and path.name != "template"
        and (path / APPROVAL_MARKER).is_file()
    )


def profile_path(repo_path: str, root: Path | None = None) -> Path:
    repository = Path(repo_path).expanduser().resolve(strict=True)
    if not repository.is_dir():
        raise ValueError(f"Target repository is not a directory: {repository}")

    if not repository.name:
        raise ValueError("Target repository must have a folder name.")
    return (root if root is not None else profiles_root()) / repository.name


def load_profile(repo_path: str, profiles_root: Path | None = None) -> tuple[Path, list[tuple[str, str]]]:
    profile_dir = profile_path(repo_path, profiles_root)
    if not profile_dir.is_dir() or not (profile_dir / "profile.yaml").is_file():
        raise FileNotFoundError(
            f"No local profile for {profile_dir.name}. Onboard it into {profile_dir}."
        )
    if not (profile_dir / APPROVAL_MARKER).is_file():
        raise PermissionError(
            f"Profile for {profile_dir.name} is a review draft. Approve it before loading."
        )

    contents = []
    for filename in KNOWLEDGE_FILES:
        path = profile_dir / filename
        if path.is_file():
            contents.append((filename, path.read_text(encoding="utf-8")))
    return profile_dir, contents


def main() -> int:
    parser = argparse.ArgumentParser(prog="qa-agent", description=__doc__)
    parser.add_argument("--profiles-dir", help="absolute profile-store path (overrides UQA_PROFILES_DIR)")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("profiles", help="list locally stored repository profiles")
    profile_parser = commands.add_parser("profile", help="load profile knowledge for a target repository")
    profile_parser.add_argument("--repo", required=True, help="path to the external target repository")
    path_parser = commands.add_parser("profile-path", help="print the profile destination without loading it")
    path_parser.add_argument("--repo", required=True, help="path to the external target repository")
    args = parser.parse_args()

    try:
        root = absolute_directory(args.profiles_dir) if args.profiles_dir else profiles_root()
        if args.command == "profile-path":
            print(profile_path(args.repo, root))
            return 0
        if args.command == "profiles":
            profiles = available_profiles(root)
            if not profiles:
                print("No repository profiles found.")
            for path in profiles:
                print(path.name)
            return 0

        profile_dir, contents = load_profile(args.repo, root)
        print(f"Target repository: {Path(args.repo).expanduser().resolve()}")
        print(f"Profile directory: {profile_dir}")
        for name, content in contents:
            print(f"\n--- {name} ---\n{content.rstrip()}")
        return 0
    except (OSError, ValueError) as error:
        print(f"qa-agent: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
