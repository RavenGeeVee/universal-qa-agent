# GitHub Copilot adapter

Install the native plugin in Copilot CLI:

```sh
copilot plugin marketplace add RavenGeeVee/universal-qa-agent
copilot plugin install universal-qa-agent@universal-qa-local
```

Copilot CLI reads the shared `.claude-plugin/marketplace.json` catalog and installs `plugins/universal-qa-agent`, using its portable root `plugin.json` and shared `skills/`. See the [Copilot CLI plugin reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-plugin-reference). This installation applies to CLI sessions; it does not install a VS Code extension or configure cloud agents.

For personal skills in supported local clients, run `python3 scripts/install_agent_skills.py --agent copilot` on macOS/Linux or `py -3 scripts/install_agent_skills.py --agent copilot` on Windows from this checkout. The installer links the shared skills into `~/.copilot/skills`, with a Windows junction fallback, and refuses unrelated occupied paths. Keep the checkout available. Choose one method per host to avoid duplicate skills.

Start a fresh agent session in the target repository. Ask Copilot to use `qa-onboard-repo` to prepare a repository profile for review. After approval, ask it to use `jira-test-generator` for a Jira key. Copilot selects relevant skills from their descriptions; the shared skill files define the same profile store, evidence requirements, approval gates, and validation behavior as the Codex adapter.

Jira retrieval, repository editing, and command execution depend on the Copilot client and its available tools and permissions. Prepare Python 3.10+ with `requirements-core.txt`; installation does not install Python dependencies or change host configuration. Update the native installation with `copilot plugin marketplace update universal-qa-local`, then `copilot plugin update universal-qa-agent` and restart the session.

The skill itself does not enforce tool-level approval. Report `approval_gate` as unavailable unless the active Copilot surface demonstrably blocks writes and command execution pending approval. Otherwise, pause before each scoped action for direct user approval and report the instruction-level limitation.

Profiles use the discovered Universal QA Agent source checkout's `repo-profiles` directory. Set an absolute `UQA_PROFILES_DIR` or `--profiles-dir` to choose another store. Keep the same store and repository identity across agents to share approved profiles.

See the [installation and usage guide](../../README.md#github-copilot-installation) for prerequisites and agent-specific steps, and [environment setup](../../docs/local-development.md) for Python, Windows, and shared profiles.
