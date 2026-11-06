---
name: qa-onboard-repo
description: Inspect the current or specified automation repository, identify its test framework and reusable patterns, and draft an evidence-backed repository profile in persistent local storage.
---

# Onboard an automation repository

Use the repository open in the active coding agent as the target unless the user provides another path. Explicit user instructions take precedence over this workflow.

## Identity and validation safeguards

Use profile schema 1.1 and populate `repository.identity`. Prefer a normalized credential-free Git remote identity; otherwise use the canonical repository root. Never identify a profile by folder name alone. The current helper still resolves by folder name, so inspect the profile identity before loading it and stop on missing, mismatched, or ambiguous identities. Existing version 1.0 profiles are migration drafts until identity is added and approved.

The current helper has no deterministic schema validator. Keep generated profiles explicitly marked unvalidated and do not create `.profile-approved` until deterministic validation is available and succeeds. Report this as a runtime limitation.

Resolve this loaded `SKILL.md` to its actual file location (follow symlinks for legacy skill installs). The package root is two directories above its containing skill directory. Resolve bundled `scripts/`, `schemas/`, and `repo-profiles/template/` from that root, never from the target working directory or a fixed clone path. Quote paths when constructing commands. Use Python 3.10 or newer (`python3` on macOS/Linux; `py -3` on Windows).

Profiles live outside the installed package, by default under `~/.local/share/universal-qa-agent/repo-profiles/`. `UQA_PROFILES_DIR` overrides the store with an absolute path; keep this setting consistent across workflows. Use the bundled `scripts/qa_agent.py profile-path --repo <absolute-target-path>` to print the destination. Helpers only read files and print paths. Never store knowledge in the plugin cache or copy agent files into the target. If access is denied, report the required path and request scoped access.

## Workflow

1. Resolve the target path and show it with the helper's profile destination. If an existing profile identity is missing or does not match, stop and resolve the conflict; do not rely on folder-name equality.
2. Inspect manifests, tree layout, representative tests, test configuration, data, helpers, screen/page objects, API clients, and existing execution instructions. Do not run builds or tests during onboarding.
3. Record evidence paths for language, framework, build system, test runner, BDD implementation, source layout, conventions, reusable patterns, restrictions, and commands. Leave unsupported or uncertain claims in `knowledge_gaps`.
4. If a profile exists, compare the evidence and propose only a reviewable update. Do not replace accepted profile knowledge without approval.
5. If no profile exists, create the persistent profile directory and draft `profile.yaml` using `<package-root>/schemas/repository-profile.schema.json`, including repository identity, plus `conventions.md` and `patterns.md`, in the helper's persistent profile destination. Do not create or modify files in the target repository.
6. Show the profile, identity, evidence, conventions, patterns, and unresolved gaps. Treat it as a draft until deterministic validation succeeds and the user approves it. Only then create `.profile-approved` in the profile directory.

Use `<package-root>/scripts/qa_agent.py` to list or load accepted profiles. Run it with Python 3 using the platform's launcher (`python3` on macOS/Linux; `py -3` on Windows). Pass `.` as the repository path when the active coding-agent workspace is the target. A pending draft is deliberately excluded from profile loading until approved.

Before any build, test, lint, formatting, or verification command, state the exact command and wait for user approval. Never claim schema validation ran without deterministic validator evidence.

## Report

Summarize the target path, profile path/status, detected stack, inspected patterns, evidence, gaps, and whether the target repository was changed. The target should remain unchanged during onboarding.
