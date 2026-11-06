# Local helpers

Python 3.10 or newer is required. The current profile helper uses only the standard library; the planned deterministic validator will declare its local schema/YAML libraries and will not use a hosted service.

- `qa_agent.py profiles` lists approved profiles; a missing store returns an empty list.
- `qa_agent.py profile-path --repo <target>` prints the draft/approved profile destination without writing files.
- `qa_agent.py profile --repo <target>` loads profile, conventions, and patterns only when `.profile-approved` exists.

Storage defaults to `~/.local/share/universal-qa-agent/repo-profiles`. An absolute `UQA_PROFILES_DIR` overrides it; global `--profiles-dir <absolute-path>` takes precedence. The helper does not parse YAML, validate schemas, retrieve Jira issues, migrate profiles, or run target commands.

`install_agent_skills.py` links the shared root `skills/` into Claude Code (`~/.claude/skills`) and GitHub Copilot (`~/.copilot/skills`). It uses Windows junctions when symlinks are unavailable and refuses to replace occupied skill paths. Codex continues to use its plugin or `install_codex_skills.py`.

`package_plugin.py` stages an allowlisted plugin at `dist/universal-qa-agent` for the repository marketplace. It excludes private profiles, developer settings, and bytecode, and refuses to overwrite an existing package. Packaging requires approval before execution under this repository's policy.
