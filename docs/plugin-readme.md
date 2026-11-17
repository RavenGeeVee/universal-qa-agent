# Universal QA Agent

Turn Jira requirements into reviewable tests that follow your automation repository's conventions. This MIT-licensed plugin provides two shared skills for Codex, Claude Code, and supported Copilot clients:

- `qa-onboard-repo`: inspect a repository and draft a profile of its framework, conventions, and reusable patterns for approval.
- `jira-test-generator`: map a Jira issue to scenarios and coverage gaps, then implement the plan you approve. Use a verified project test-case template when available; otherwise use the bundled CSV template.

## Requirements and setup

Run this plugin locally with Git, Python 3.10+, and access to your automation repository. Install `requirements-core.txt` into a dedicated Python environment and tell the agent the absolute path to that environment's interpreter. Installing the plugin does not install Python dependencies or connect Jira. Use your host's Jira integration, or supply the issue description and acceptance criteria yourself.

After installation, ask the agent to locate this plugin's `requirements-core.txt` and show the exact dependency-installation command for approval. For example, create an environment with `python3 -m venv ~/.venvs/universal-qa-agent`, then install using that environment's Python and the absolute path to the bundled requirements file. On Windows, create the environment with `py -3 -m venv` and use its `Scripts/python.exe`.

For profile storage, keep a source checkout of [the repository](https://github.com/RavenGeeVee/universal-qa-agent) in a stable local location; its Git-ignored `repo-profiles/` is discovered automatically. Alternatively, choose a private absolute directory and supply `--profiles-dir` on every helper call, or set `UQA_PROFILES_DIR` in the agent process environment. Tell the agent your chosen store before onboarding. Plugin caches are not persistent profile stores. Do not commit profiles or credentials.

## Install

For Codex, register the marketplace:

```sh
codex plugin marketplace add RavenGeeVee/universal-qa-agent
```

Restart the ChatGPT desktop app, select **Universal QA Local** in **Plugins Directory**, and install **universal-qa-agent**. For a public directory installation, use the approved listing when available.

For Claude Code:

```sh
claude plugin marketplace add RavenGeeVee/universal-qa-agent
claude plugin install universal-qa-agent@universal-qa-local
```

For Copilot CLI:

```sh
copilot plugin marketplace add RavenGeeVee/universal-qa-agent
copilot plugin install universal-qa-agent@universal-qa-local
```

Start a fresh session in the target repository. Choose one installation method per host to avoid duplicate skills. See the [full installation guide](https://github.com/RavenGeeVee/universal-qa-agent#choose-your-installation) for personal skills in supported local editors.

## First use

In Codex, select `qa-onboard-repo` from the plugin's skill picker. In Claude Code, run `/universal-qa-agent:qa-onboard-repo`. In Copilot, request the skill by name. Ask:

```text
Onboard this repository. Show the profile, evidence, reusable patterns,
and unresolved questions for approval. Do not run builds or tests.
```

After approving the profile, select `jira-test-generator` in Codex, run `/universal-qa-agent:jira-test-generator QA-123` in Claude Code, or request it by name in Copilot:

```text
Analyze QA-123 using the approved repository profile. Show requirements,
scenarios, coverage gaps, and the proposed implementation plan.
Wait for approval before editing code or running verification commands.
```

The skills ask for approval before implementation and exact verification commands. Enforcement depends on your host's tools and permissions. The helper checks repository identity and content-bound profile approval; it does not run an autonomous service. Private profile drafts, accepted knowledge, feedback, generated plans, test-case documents, and target code are described in the [artifact guide](https://github.com/RavenGeeVee/universal-qa-agent/blob/main/docs/artifacts.md).

## Support and data handling

Report a sanitized issue through [GitHub Issues](https://github.com/RavenGeeVee/universal-qa-agent/issues). Keep repository names, paths, tickets, credentials, and private test data out of public reports. Read the [data-handling notice](https://github.com/RavenGeeVee/universal-qa-agent/blob/main/docs/privacy.md). Your chosen agent and connected services process the context you provide under their own policies.

Project documentation and updates: [RavenGeeVee/universal-qa-agent](https://github.com/RavenGeeVee/universal-qa-agent). License: [MIT](LICENSE).
