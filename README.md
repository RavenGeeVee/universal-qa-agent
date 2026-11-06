# Universal QA Agent

An agent-agnostic QA workflow for turning Jira requirements into tests that follow an existing automation repository's conventions. Codex has a plugin adapter; Claude Code and GitHub Copilot use the same shared Agent Skills. Each host supplies its own model, tools, and file editing; no separate LLM API or hosted service is required.

## Install and use

The Git-backed marketplace loads the clean, versioned package in `plugins/universal-qa-agent`. Refresh it from the canonical sources with `scripts/package_plugin.py` before releasing changes. For personal skill links, use `scripts/install_agent_skills.py --agent claude`, `--agent copilot`, or `--agent codex`; omitting `--agent` installs Claude Code and GitHub Copilot as before. See [local setup](docs/local-development.md). Python 3.10 or newer is required for the bundled helpers.

1. Install the `universal-qa-agent` plugin and open your target automation repository in Codex.
2. Invoke `qa-onboard-repo`. Review the identity and evidence-backed profile; approve it through the helper after local schema validation succeeds.
3. Invoke its `jira-test-generator` skill with a Jira key. Jira retrieval uses your active host connection; otherwise supply the ticket content.
4. Review the scenarios and change plan, then explicitly approve target code changes.
5. Approve each exact verification command before execution. Review changes, traceability, results, and unresolved gaps.

## Package layout

- `plugin.json` identifies the portable Agent Plugins package; `skills/` contains the two workflows.
- `scripts/qa_agent.py` resolves identity-scoped profiles, validates local artifacts, and records content-bound profile approval. It does not execute target commands or retrieve Jira issues.
- `schemas/` defines repository identity, requirement/capability provenance, test cases, knowledge proposals, approval scopes, automation plans, and validation-result contracts. `requirements-core.txt` supplies local YAML and JSON Schema libraries.
- `repo-profiles/template/` provides an empty profile template. Other profiles in a development checkout are private legacy drafts, ignored by Git; do not distribute them.
- `core/` defines the portable identity, validation, capability, and approval boundaries. A standalone core engine is not implemented yet.
- `agent-adapters/` documents the Codex plugin, Claude Code skills, and GitHub Copilot skills adapters. Root `skills/` is the single workflow source.
- `tests/` contains helper, installer, and package contract tests. They require explicit command approval before running.

## Persistent knowledge

Profiles default to `~/.local/share/universal-qa-agent/repo-profiles/`, independently of the plugin installation. Set `UQA_PROFILES_DIR` to an absolute path to override it. The helper also accepts global `--profiles-dir` before a subcommand. Approved profiles require a `.profile-approved` record matching repository identity and exact profile contents; drafts cannot be loaded. Profiles use a normalized Git remote plus target subpath, or canonical local path when no usable remote exists. See [P0 design controls](docs/p0-design-controls.md).

Plugin refreshes replace package files without replacing the separate profile store. Existing checkout profiles are not moved or approved automatically. Profiles before schema 1.2 need identity migration and explicit approval before loading.

## Workflow and safety

See [onboarding](docs/repository-onboarding.md), [Jira automation](docs/jira-automation.md), and [knowledge maintenance](docs/knowledge-maintenance.md). Target edits, exact validation commands, and accepted knowledge updates require scoped approval. Current adapters request approval through host interactions; there is not yet a universal tool gate. Jira authentication and external tool permissions come from the active host session and must be reported, not assumed.

The cross-agent P0 contracts and implementation gaps are documented in [P0 design controls](docs/p0-design-controls.md).
