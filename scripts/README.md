# Local helpers

Python 3.10 or newer is required. Install `requirements-core.txt` for local YAML and JSON Schema validation. No hosted service or LLM API is used.

- `qa_agent.py profiles` lists approved profiles; an absent selected store returns an empty list. Automatic discovery requires a source checkout.
- `qa_agent.py profile-path --repo <target>` prints the unique existing identity match, or a new destination named for the target repository directory, without writing files. Duplicate identities or an occupied unrelated name block selection.
- `qa_agent.py profile --repo <target>` loads profile, conventions, and patterns only when identity, schema, and content-bound approval all match.
- `qa_agent.py approve-profile --repo <target> --approval-reference <user-approval>` validates a draft and records the explicit approval after the workflow has presented it to the user.
- `qa_agent.py validate --schema <bundled-schema.schema.json> --input <artifact>` validates a JSON/YAML artifact; `--related` adds artifacts for supported cross-checks.

Storage resolves to the source checkout's `repo-profiles` directory. Global `--profiles-dir <absolute-path>` takes precedence over `UQA_PROFILES_DIR`; otherwise the helper checks its own source root, resolved personal skill links, then a recursive home-directory search for `universal-qa-agent`. Candidates require the installer and profile-template markers; plugin/release copies and cache/dependency directories are excluded. No match or multiple matches require an explicit store. Discovery neither writes nor migrates profiles. See [discovery details](../docs/local-development.md#shared-profiles-across-agents). Profile folders use readable repository names, while identity keys remain inside the profile and approval record. Folder-only renames preserve approval. The helper does not retrieve Jira issues, generate test code, move profiles automatically, or run target commands. Jira analysis and code generation remain agent workflows; helper validation is deterministic and local.

`install_agent_skills.py` owns shared skill installation. With no arguments it preserves the existing default: Claude Code (`~/.claude/skills`) and GitHub Copilot (`~/.copilot/skills`). Select one host with `--agent claude`, `--agent copilot`, or `--agent codex` (standalone links in `~/.agents/skills`). It preserves Windows junction fallback, preflights all selected destinations before changes, and refuses unrelated occupied paths. Codex selection also migrates legacy Codex skill links.

Codex plugin installation is separate; avoid enabling duplicate plugin and standalone skills.

`package_plugin.py` writes an allowlisted plugin at `plugins/universal-qa-agent` for the repository marketplace. Commit that release folder with the catalog so GitHub installations receive the package. It excludes private profiles, developer settings, and bytecode, and refuses to overwrite an existing package. Packaging requires approval before execution under this repository's policy.
