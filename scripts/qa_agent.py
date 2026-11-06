#!/usr/bin/env python3
"""Local, deterministic helpers for Universal QA Agent skills."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
from pathlib import PurePosixPath, PureWindowsPath
import re
import secrets
import subprocess
import sys
from urllib.parse import urlsplit

try:
    import yaml
    from jsonschema import Draft202012Validator, FormatChecker
except ImportError:
    yaml = None
    Draft202012Validator = None
    FormatChecker = None

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "schemas"
APPROVAL_MARKER = ".profile-approved"
KNOWLEDGE_FILES = ("profile.yaml", "conventions.md", "patterns.md")


def profiles_root(override=None):
    value = override or os.environ.get("UQA_PROFILES_DIR") or "~/.local/share/universal-qa-agent/repo-profiles"
    path = Path(value).expanduser()
    if not path.is_absolute():
        raise ValueError("profile store must be an absolute path")
    return path.resolve()


def _git(path, *args):
    result = subprocess.run(["git", "-C", str(path), *args], capture_output=True, text=True, check=False)
    return result.stdout.strip() if result.returncode == 0 else ""


def repository_identity(repo, remote=None):
    repo = Path(repo).expanduser().resolve(strict=True)
    git_root = _git(repo, "rev-parse", "--show-toplevel")
    if git_root:
        git_root = Path(git_root).resolve()
        scope = repo.relative_to(git_root).as_posix() or "."
        remotes = _git(repo, "remote").splitlines()
        if not remote and "origin" not in remotes and len(remotes) > 1:
            raise ValueError("multiple Git remotes found; select the repository identity with --remote")
        selected = remote or ("origin" if "origin" in remotes else remotes[0] if len(remotes) == 1 else None)
        if remote and remote not in remotes:
            raise ValueError(f"remote not found: {remote}")
        url = _git(repo, "remote", "get-url", selected) if selected else ""
        normalized = _normalize_remote(url) if url else ""
        if normalized:
            kind, value = "git_remote", normalized
        else:
            kind, value, scope = "filesystem_path", str(repo), "."
    else:
        kind, value, scope = "filesystem_path", str(repo), "."
    return _identity(kind, value, scope)


def _identity(kind, value, scope):
    digest = hashlib.sha256(f"{kind}\0{value}\0{scope}".encode("utf-8")).hexdigest()
    return {"kind": kind, "value": value, "scope": scope, "key": f"sha256:{digest}"}


def _normalize_remote(url):
    url = re.sub(r"[?#].*$", "", url.strip())
    if url.startswith("git@") or ("://" not in url and re.match(r"^[^/]+:.+", url)):
        host, path = url.split(":", 1)
        host = host.rsplit("@", 1)[-1]
    else:
        parsed = urlsplit(url)
        host = parsed.hostname or ""
        if parsed.port:
            host = f"{host}:{parsed.port}"
        path = parsed.path.lstrip("/")
    if not host or "/" not in path:
        return ""
    path = path.rstrip("/")
    if path.endswith(".git"):
        path = path[:-4]
    return f"{host.lower()}/{path}"


def profile_path(repo, store=None, remote=None):
    identity = repository_identity(repo, remote)
    return profiles_root(store) / f"repo-{identity['key'][7:]}"


def available_profiles(store=None):
    root = profiles_root(store)
    if not root.is_dir():
        return []
    approved = []
    for path in root.glob("repo-*"):
        try:
            profile = _load_yaml(path / "profile.yaml")
            identity = profile["repository"]["identity"]
            if identity != _identity(identity["kind"], identity["value"], identity["scope"]):
                continue
            _verify_profile(path, identity)
            if path.name == f"repo-{identity['key'][7:]}" and (path / APPROVAL_MARKER).is_file():
                approved.append(path)
        except (OSError, ValueError, KeyError, TypeError, RuntimeError, json.JSONDecodeError):
            continue
    return sorted(approved)


def _profile_files(directory):
    files = {}
    for name in KNOWLEDGE_FILES:
        path = directory / name
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"missing or unsafe profile file: {name}")
        files[name] = path.read_bytes()
    return files


def _content_digest(files):
    digest = hashlib.sha256()
    for name, content in sorted(files.items()):
        digest.update(name.encode("utf-8") + b"\0" + content + b"\0")
    return "sha256:" + digest.hexdigest()


def _load_yaml(path):
    if yaml is None:
        raise RuntimeError("install local dependencies: pip install -r requirements-core.txt")
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ValueError(f"invalid YAML in {path.name}: {exc}") from exc


def _validate(data, schema_name):
    if Draft202012Validator is None:
        raise RuntimeError("install local dependencies: pip install -r requirements-core.txt")
    if Path(schema_name).name != schema_name or not schema_name.endswith(".schema.json"):
        raise ValueError("schema must be a bundled schema filename")
    schema_path = SCHEMA_DIR / schema_name
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    return sorted(validator.iter_errors(data), key=lambda e: list(map(str, e.absolute_path)))


def _verify_profile(directory, identity):
    marker_path = directory / APPROVAL_MARKER
    if marker_path.is_symlink():
        raise ValueError("unsafe profile approval marker")
    files = _profile_files(directory)
    marker = json.loads(marker_path.read_text(encoding="utf-8"))
    profile = _load_yaml(directory / "profile.yaml")
    errors = _validate(profile, "repository-profile.schema.json")
    if errors:
        raise ValueError("invalid profile: " + "; ".join(f"/{'/'.join(map(str, e.absolute_path))}: {e.message}" for e in errors))
    if profile["repository"]["identity"] != identity or marker.get("identity_key") != identity["key"]:
        raise PermissionError("profile identity does not match target repository")
    if identity != _identity(identity["kind"], identity["value"], identity["scope"]):
        raise PermissionError("profile identity key is invalid")
    if marker.get("content_digest") != _content_digest(files):
        raise PermissionError("approved profile changed since approval; review and approve it again")
    return [(name, files[name].decode("utf-8")) for name in KNOWLEDGE_FILES]


def load_profile(repo, store=None, remote=None):
    identity = repository_identity(repo, remote)
    directory = profiles_root(store) / f"repo-{identity['key'][7:]}"
    if not (directory / APPROVAL_MARKER).is_file():
        raise FileNotFoundError(f"no approved profile for {repo}; expected {directory}")
    return directory, _verify_profile(directory, identity)


def approve_profile(repo, approval_reference, store=None, remote=None):
    approval_reference = approval_reference.strip()
    if not approval_reference:
        raise ValueError("approval reference must describe the user's explicit approval")
    identity = repository_identity(repo, remote)
    directory = profiles_root(store) / f"repo-{identity['key'][7:]}"
    files = _profile_files(directory)
    profile = _load_yaml(directory / "profile.yaml")
    errors = _validate(profile, "repository-profile.schema.json")
    if errors:
        raise ValueError("profile validation failed: " + "; ".join(f"/{'/'.join(map(str, e.absolute_path))}: {e.message}" for e in errors))
    if profile["repository"]["identity"] != identity:
        raise PermissionError("draft profile identity does not match target repository")
    if identity != _identity(identity["kind"], identity["value"], identity["scope"]):
        raise PermissionError("draft profile identity key is invalid")
    record = {"identity_key": identity["key"], "content_digest": _content_digest(files),
              "approval_reference": approval_reference, "approved_at": datetime.now(timezone.utc).isoformat()}
    temporary = directory / f"{APPROVAL_MARKER}.{secrets.token_hex(8)}.tmp"
    with temporary.open("x", encoding="utf-8") as output:
        output.write(json.dumps(record, sort_keys=True) + "\n")
    temporary.replace(directory / APPROVAL_MARKER)


def validate_artifact(schema, input_path, related=None):
    source = Path(input_path)
    data = _load_yaml(source) if source.suffix.lower() in (".yaml", ".yml") else json.loads(source.read_text(encoding="utf-8"))
    errors = _validate(data, schema)
    if errors:
        return _render_errors(errors)
    related_data = [(_load_yaml(Path(path)) if Path(path).suffix.lower() in (".yaml", ".yml") else json.loads(Path(path).read_text(encoding="utf-8"))) for path in (related or [])]
    _cross_validate(schema, data, related_data, errors)
    if schema == "knowledge-proposal.schema.json" and data.get("classification") == "universal":
        identities = {e.get("repository_identity_key") for e in data.get("evidence", []) if e.get("source") == "repository"}
        if len(identities) < 2:
            errors.append(_error("/evidence", "universal knowledge requires evidence from at least two repository identities"))
    if schema == "knowledge-proposal.schema.json" and data.get("classification") == "repository_specific":
        identity = data.get("repository_identity_key")
        if any(e.get("source") == "repository" and e.get("repository_identity_key") != identity for e in data.get("evidence", [])):
            errors.append(_error("/evidence", "repository-specific evidence must match the proposal repository identity"))
    if schema == "automation-plan.schema.json":
        payload = {key: data[key] for key in ("schema_version", "issue_key", "items", "approval_required", "unresolved_gaps")}
        payload["scopes"] = data["approval"]["scopes"]
        if data["approval"]["approval_digest"] != _json_digest(payload):
            errors.append(_error("/approval/approval_digest", "approval digest does not match the plan and scopes"))
    if schema == "knowledge-proposal.schema.json":
        payload = {key: value for key, value in data.items() if key != "approval"}
        if data["approval"]["approval_digest"] != _json_digest(payload):
            errors.append(_error("/approval/approval_digest", "approval digest does not match the knowledge proposal"))
    return _render_errors(errors)


def _render_errors(errors):
    return [{"path": "/" + "/".join(map(str, e.absolute_path)), "code": getattr(e, "code", "SCHEMA_VALIDATION"), "message": e.message} for e in errors]


def _json_digest(value):
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def _cross_validate(schema, data, related, errors):
    if schema == "repository-profile.schema.json":
        identity = data["repository"]["identity"]
        if identity != _identity(identity["kind"], identity["value"], identity["scope"]):
            errors.append(_error("/repository/identity/key", "identity key does not match kind, value, and scope"))
    if schema == "requirement-analysis.schema.json":
        status = data["issue"]["retrieval"]["status"]
        kinds = {s["kind"] for s in data["issue"]["sources"]}
        jira_kinds = {"jira_description", "acceptance_criteria", "comment", "linked_issue"}
        missing = data["issue"]["retrieval"]["unavailable_sources"]
        valid = {"retrieved": bool(kinds & jira_kinds) and not missing, "user_provided": "user_input" in kinds and not (kinds & jira_kinds) and not missing,
                 "partial": bool(kinds) and bool(missing),
                 "unavailable": not kinds}[status]
        if not valid:
            errors.append(_error("/issue/retrieval/status", "retrieval status conflicts with recorded sources"))
        all_statements = data.get("requirements", []) + data.get("acceptance_criteria", [])
        ids = [item.get("id") for item in all_statements]
        if len(ids) != len(set(ids)):
            errors.append(_error("/requirements", "IDs must be unique across requirement and acceptance-criteria lists"))
        for field in ("requirements", "acceptance_criteria"):
            for index, item in enumerate(data.get(field, [])):
                if not item.get("sources"):
                    errors.append(_error(f"/{field}/{index}/sources", "requirement needs source evidence"))
        if len(related) > 0:
            cases = related[0].get("cases", [])
            ids = {item.get("id") for item in data.get("requirements", []) + data.get("acceptance_criteria", [])}
            for i, case in enumerate(cases):
                for requirement_id in case.get("requirement_ids", []):
                    if requirement_id not in ids:
                        errors.append(_error(f"/related/cases/{i}/requirement_ids", f"unknown requirement ID {requirement_id}"))
    if schema == "automation-plan.schema.json":
        cases = related[0].get("cases", []) if related else []
        ids = {case.get("id") for case in cases}
        referenced = [item.get("test_case_id") for item in data.get("items", [])]
        if related and set(referenced) != ids:
            errors.append(_error("/items", "plan must include exactly one decision for each test case"))
        if len(referenced) != len(set(referenced)):
            errors.append(_error("/items", "each test case may appear only once in the plan"))
        for i, item in enumerate(data.get("items", [])):
            if related and item.get("test_case_id") not in ids:
                errors.append(_error(f"/items/{i}/test_case_id", "unknown test case"))
            for path in item.get("target_files", []):
                if "\\" in path or PurePosixPath(path).is_absolute() or PureWindowsPath(path).is_absolute() or PureWindowsPath(path).drive or ".." in PurePosixPath(path).parts:
                    errors.append(_error(f"/items/{i}/target_files", "target paths must be normalized repository-relative paths"))
        targets = {path for item in data.get("items", []) if item.get("action") in ("create", "extend") for path in item.get("target_files", [])}
        approved = {s.get("resource") for s in data.get("approval", {}).get("scopes", []) if s.get("kind") == "target_edit"}
        if targets != approved:
            errors.append(_error("/approval/scopes", "target edit scopes must exactly match create/extend target files"))
        if len(related) > 1:
            profile = related[1]
            commands = {tuple(c["argv"]): c["working_directory"] for c in profile.get("commands", {}).get("validation", [])}
            for i, scope in enumerate(data.get("approval", {}).get("scopes", [])):
                if scope.get("kind") == "validation_command" and commands.get(tuple(scope.get("argv", []))) != scope.get("working_directory"):
                    errors.append(_error(f"/approval/scopes/{i}", "command scope does not match a profiled validation command"))
        elif any(scope.get("kind") == "validation_command" for scope in data.get("approval", {}).get("scopes", [])):
            errors.append(_error("/approval/scopes", "validation command scopes require the repository profile for comparison"))
    if schema == "test-case.schema.json" and related:
        analysis = related[0]
        ids = {item.get("id") for item in analysis.get("requirements", []) + analysis.get("acceptance_criteria", [])}
        for i, case in enumerate(data.get("cases", [])):
            for requirement_id in case.get("requirement_ids", []):
                if requirement_id not in ids:
                    errors.append(_error(f"/cases/{i}/requirement_ids", f"unknown requirement ID {requirement_id}"))


def _error(path, message):
    return type("ValidationError", (), {"absolute_path": path.strip("/").split("/") if path != "/" else [], "code": "CROSS_ARTIFACT", "message": message})()


def main(argv=None):
    parser = argparse.ArgumentParser(prog="qa-agent")
    parser.add_argument("--profiles-dir", help="absolute local profile store")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("profiles")
    for command in ("profile-path", "profile", "approve-profile"):
        item = sub.add_parser(command)
        item.add_argument("--repo", required=True)
        item.add_argument("--remote")
        if command == "approve-profile":
            item.add_argument("--approval-reference", required=True, help="brief reference to the user's explicit approval")
    validate = sub.add_parser("validate")
    validate.add_argument("--schema", required=True)
    validate.add_argument("--input", required=True)
    validate.add_argument("--related", action="append", default=[], help="related artifacts; plan order is test cases, then profile YAML")
    args = parser.parse_args(argv)
    try:
        store = profiles_root(args.profiles_dir) if args.profiles_dir else None
        if args.command == "profiles":
            print(json.dumps([str(path) for path in available_profiles(store)], indent=2))
        elif args.command == "profile-path":
            print(profile_path(args.repo, store, args.remote))
        elif args.command == "profile":
            _, contents = load_profile(args.repo, store, args.remote)
            print("\n".join(f"--- {name} ---\n{content}" for name, content in contents))
        elif args.command == "approve-profile":
            approve_profile(args.repo, args.approval_reference, store, args.remote)
        else:
            errors = validate_artifact(args.schema, args.input, args.related)
            print(json.dumps({"schema_version": "1.0", "artifact": args.input, "schema": args.schema, "valid": not errors, "errors": errors}, indent=2))
            return 0 if not errors else 1
        return 0
    except (OSError, ValueError, PermissionError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"qa-agent: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
