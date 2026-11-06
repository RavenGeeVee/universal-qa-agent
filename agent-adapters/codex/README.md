# Codex adapter

The portable plugin packages the two workflows in root [`skills/`](../../skills): `qa-onboard-repo` and `jira-test-generator`. Root `plugin.json` supplies package identity; the repository marketplace makes it discoverable for local installation.

Skills resolve bundled helpers and schemas from their loaded file location. Persistent knowledge defaults to `~/.local/share/universal-qa-agent/repo-profiles`, with `UQA_PROFILES_DIR` as an absolute-path override. Jira access and editing permissions depend on the active Codex session. No MCP server or separate LLM API is bundled.

See [installation and skill setup](../../docs/local-development.md). For standalone skills, run `python3 scripts/install_agent_skills.py --agent codex`. Avoid enabling duplicate standalone and plugin skills in Codex.

The skills-only plugin does not itself enforce scoped tool approvals. Report the host gate as unavailable unless the active Codex sandbox/permission configuration blocks writes and command execution pending approval. Otherwise, pause before each scoped action for direct user approval and disclose the instruction-level limitation.
