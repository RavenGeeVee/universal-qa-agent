# Claude Code adapter

Claude Code loads the shared Agent Skills from `~/.claude/skills`. Run `python3 scripts/install_agent_skills.py --agent claude` on macOS/Linux or `py -3 scripts/install_agent_skills.py --agent claude` on Windows from this checkout. The installer creates directory symlinks, with a Windows junction fallback, and refuses to replace existing nonmatching skill paths.

In Claude Code, invoke `/qa-onboard-repo` to create a repository profile draft and `/jira-test-generator` to prepare Jira automation. Both skills use the same profile store and approval gates as the Codex adapter.

Claude Code has no Jira or target-repository access granted by this adapter. The active session must provide the needed tools and permissions.

The skill itself does not enforce tool-level approval. Report `approval_gate` as unavailable unless the active Claude Code permission configuration demonstrably blocks writes and command execution pending approval. Otherwise, pause before each scoped action for direct user approval and report the instruction-level limitation.

Profiles use the discovered Universal QA Agent source checkout's `repo-profiles` directory. Set an absolute `UQA_PROFILES_DIR` or `--profiles-dir` to choose another store. Keep the same store and repository identity across agents to share approved profiles.

See the [installation and usage guide](../../README.md#claude-code-installation) for prerequisites and agent-specific steps, and [environment setup](../../docs/local-development.md) for Python, Windows, and shared profiles.
