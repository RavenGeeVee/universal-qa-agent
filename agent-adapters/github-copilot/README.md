# GitHub Copilot adapter

GitHub Copilot loads personal Agent Skills from `~/.copilot/skills`. Run `python3 scripts/install_agent_skills.py --agent copilot` on macOS/Linux or `py -3 scripts/install_agent_skills.py --agent copilot` on Windows from this checkout. The installer creates directory symlinks, with a Windows junction fallback, and refuses to replace existing nonmatching skill paths.

Ask Copilot to onboard the current automation repository or generate automation from a Jira issue. Copilot selects relevant skills from their descriptions; the shared skill files define the same profile store, evidence requirements, approval gates, and validation behavior as the Codex adapter.

Jira retrieval, repository editing, and command execution depend on the Copilot surface and its available tools and permissions.

The skill itself does not enforce tool-level approval. Report `approval_gate` as unavailable unless the active Copilot surface demonstrably blocks writes and command execution pending approval. Otherwise, pause before each scoped action for direct user approval and report the instruction-level limitation.
