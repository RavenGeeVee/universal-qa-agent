# Claude Code adapter

Install the native plugin from the repository marketplace:

```sh
claude plugin marketplace add RavenGeeVee/universal-qa-agent
claude plugin install universal-qa-agent@universal-qa-local
```

The root `.claude-plugin/marketplace.json` catalog points to the shared `plugins/universal-qa-agent` release, whose `.claude-plugin/plugin.json` supplies Claude metadata. Root `skills/` remains the canonical workflow source. See [Claude Code's marketplace documentation](https://code.claude.com/docs/en/plugin-marketplaces).

In a fresh Claude Code session in the target repository, invoke `/universal-qa-agent:qa-onboard-repo` to create a profile draft. After profile approval, invoke `/universal-qa-agent:jira-test-generator QA-123`. Both skills use the same profile store and approval gates as the Codex adapter.

For standalone personal skills instead, run `python3 scripts/install_agent_skills.py --agent claude` on macOS/Linux or `py -3 scripts/install_agent_skills.py --agent claude` on Windows from this checkout. The installer links the shared skills into `~/.claude/skills`, with a Windows junction fallback, and refuses to replace unrelated occupied paths. Invoke `/qa-onboard-repo` and `/jira-test-generator QA-123` for this installation. Choose one method to avoid duplicate skills.

The active Claude Code session supplies Jira tools, repository access, and permissions. Prepare Python 3.10+ with `requirements-core.txt`; plugin installation does not install Python packages or configure host connections.

The skill itself does not enforce tool-level approval. Report `approval_gate` as unavailable unless the active Claude Code permission configuration demonstrably blocks writes and command execution pending approval. Otherwise, pause before each scoped action for direct user approval and report the instruction-level limitation.

Profiles use the discovered Universal QA Agent source checkout's `repo-profiles` directory. Set an absolute `UQA_PROFILES_DIR` or `--profiles-dir` to choose another store. Keep the same store and repository identity across agents to share approved profiles.

See the [installation and usage guide](../../README.md#claude-code-installation) for prerequisites and agent-specific steps, and [environment setup](../../docs/local-development.md) for Python, Windows, and shared profiles.
