# Local helpers

Python 3.10 or newer is required. Install `requirements-core.txt` for local YAML and JSON Schema validation. No hosted service or LLM API is used.

- `qa_agent.py profiles` lists approved profiles; a missing store returns an empty list.
- `qa_agent.py profile-path --repo <target>` prints the draft/approved profile destination without writing files.
- `qa_agent.py profile --repo <target>` loads profile, conventions, and patterns only when identity, schema, and content-bound approval all match.
- `qa_agent.py approve-profile --repo <target> --approval-reference <user-approval>` validates a draft and records the explicit approval after the workflow has presented it to the user.
- `qa_agent.py validate --schema <bundled-schema.schema.json> --input <artifact>` validates a JSON/YAML artifact; `--related` adds artifacts for supported cross-checks.

Storage defaults to `~/.local/share/universal-qa-agent/repo-profiles`. An absolute `UQA_PROFILES_DIR` overrides it; global `--profiles-dir <absolute-path>` takes precedence. The helper does not retrieve Jira issues, generate test code, migrate legacy profiles, or run target commands. Jira analysis and code generation remain agent workflows; helper validation is deterministic and local.

`install_agent_skills.py` owns shared skill installation. With no arguments it preserves the existing default: Claude Code (`~/.claude/skills`) and GitHub Copilot (`~/.copilot/skills`). Select one host with `--agent claude`, `--agent copilot`, or `--agent codex` (standalone links in `~/.agents/skills`). It preserves Windows junction fallback, preflights all selected destinations before changes, and refuses unrelated occupied paths. Codex selection also migrates legacy Codex skill links.

Codex plugin installation is separate; avoid enabling duplicate plugin and standalone skills.

`package_plugin.py` stages an allowlisted plugin at `dist/universal-qa-agent` for the repository marketplace. It excludes private profiles, developer settings, and bytecode, and refuses to overwrite an existing package. Packaging requires approval before execution under this repository's policy.
