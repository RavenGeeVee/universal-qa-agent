---
name: qa-onboard-repo
description: Inspect the current or specified automation repository, identify its test framework and reusable patterns, and draft an evidence-backed repository profile in persistent local storage.
---

# Onboard an automation repository

Use the repository open in the active coding agent as the target unless the user provides another path. Explicit user instructions take precedence over this workflow.

## Identity and validation safeguards

Use profile schema 1.2 and populate scoped `repository.identity`. Prefer a normalized credential-free Git remote identity; otherwise use the canonical repository root. Git identity includes the target's path relative to the repository root, so monorepo subprojects have separate profiles. Never identify a profile by folder name alone. If multiple remotes exist without `origin`, choose one explicitly with `--remote`; otherwise stop rather than guessing. Existing pre-1.2 profiles are migration drafts until identity is added and approved.

The bundled helper validates profile YAML against the local Draft 2020-12 schema. After showing the draft, use `approve-profile --approval-reference "<brief record of the user's explicit approval>"` only after the user approves it. The approval record binds the repository identity and exact contents of `profile.yaml`, `conventions.md`, and `patterns.md`.

Resolve this loaded `SKILL.md` to its actual file location (follow symlinks for legacy skill installs). The package root is two directories above its containing skill directory. Resolve bundled `scripts/`, `schemas/`, and `repo-profiles/template/` from that root, never from the target working directory or a fixed clone path. Quote paths when constructing commands. Use Python 3.10 or newer (`python3` on macOS/Linux; `py -3` on Windows).

Use the bundled `scripts/qa_agent.py profile-path --repo <absolute-target-path>` to resolve storage before writing a profile. It uses the source checkout's `repo-profiles/`: the running source checkout first, then resolved personal skill links, then a search for a valid `universal-qa-agent` source checkout under the user's home directory. Plugin-cache and packaged release copies are not source checkouts. Multiple matches require explicit selection; missing checkouts require a source location or override. Do not invent a storage path or fall back to another default.

An absolute `--profiles-dir` takes precedence over `UQA_PROFILES_DIR`; keep any override consistent across workflows. The helper prints a repository-named destination without creating it. New profiles use the target repository folder name; existing human-readable folders are located by the identity stored inside profile.yaml. Keep exactly one profile per identity. On a name collision, ask for a descriptive folder rename or a separate store rather than overwriting another profile. Keep private profiles in the selected checkout's Git-ignored `repo-profiles/`, never in the plugin cache. Existing profiles in other stores are not moved automatically. If access is denied, report the required path and request scoped access.

## Workflow

1. Resolve the target path and show it with the helper's profile destination. The helper uses a readable repository-named directory and verifies identity from the profile contents; if identity selection is ambiguous, ask the user to select a remote.
2. Inspect manifests, tree layout, representative tests, test configuration, data, helpers, screen/page objects, API clients, and existing execution instructions. Do not run builds or tests during onboarding.
3. Record evidence paths for language, framework, build system, test runner, BDD implementation, source layout, conventions, reusable patterns, restrictions, and commands. Leave unsupported or uncertain claims in `knowledge_gaps`.
4. If a profile exists, compare the evidence and propose only a reviewable update. Do not replace accepted profile knowledge without approval.
5. If no profile exists, create the persistent profile directory and draft `profile.yaml` using `<package-root>/schemas/repository-profile.schema.json`, including repository identity, plus `conventions.md` and `patterns.md`, in the helper's persistent profile destination. Do not create or modify files in the target repository.
6. Show the profile, identity, evidence, conventions, patterns, and unresolved gaps. Treat it as a draft until deterministic validation succeeds and the user approves it. Then run `approve-profile` with a concise approval reference; it writes a content-bound `.profile-approved` record.

Use `<package-root>/scripts/qa_agent.py` to list or load accepted profiles. Run it with Python 3 using the platform's launcher (`python3` on macOS/Linux; `py -3` on Windows). Pass `.` as the repository path when the active coding-agent workspace is the target. A pending draft is deliberately excluded from profile loading until approved.

Before any build, test, lint, formatting, or verification command, state the exact command and wait for user approval. Do not claim profile validation unless the bundled validator succeeds.

## Report

Summarize the target path, profile path/status, detected stack, inspected patterns, evidence, gaps, and whether the target repository was changed. The target should remain unchanged during onboarding.
