# Installation and operation guide

Universal QA Agent provides the same two workflows through a Codex plugin or personal skills for Codex, Claude Code, and GitHub Copilot. Install on the machine where the coding agent runs, then open any target automation repository in that agent. The [README](../README.md) gives per-agent commands and first-use prompts; this guide covers environment setup and operation.

## Prerequisites

- Git and Python 3.10 or newer.
- An installed, signed-in coding agent supporting local Agent Skills or Codex plugins.
- Read access to the target repository and write access to the local profile store. Implementation additionally needs target-file write access.
- A connected Jira integration in the active session, or the issue key, description, and acceptance criteria supplied in the request.

Clone into a stable location:

```sh
git clone https://github.com/RavenGeeVee/universal-qa-agent.git
cd universal-qa-agent
```

The source checkout holds the shared skills and installers. Personal installation creates links to that checkout; keep the whole checkout available so skills can resolve their helper and schemas.

Examples use standard command names. If you use RTK, prefix supported shell commands with `rtk`. No installation, dependency, or verification command is run merely by reading this guide.

## Python environment

Use a dedicated environment for PyYAML and jsonschema. On macOS/Linux, from the checkout:

```sh
python3 -m venv ~/.venvs/universal-qa-agent
source ~/.venvs/universal-qa-agent/bin/activate
python3 -m pip install -r requirements-core.txt
```

Launch a terminal-based agent from that activated shell. For a GUI agent or existing editor process, specify the helper interpreter explicitly in your first request:

```text
Use /absolute/home/.venvs/universal-qa-agent/bin/python
for Universal QA Agent helper commands.
```

Replace `/absolute/home` with your actual home directory. Activating an environment in one terminal does not configure an already-running desktop app. You can also use the full interpreter path for every helper command without activation:

```sh
~/.venvs/universal-qa-agent/bin/python /absolute/path/to/universal-qa-agent/scripts/qa_agent.py profiles
```

The installed Codex plugin includes `requirements-core.txt` and its helper; a Python environment with those dependencies must still be available to the local agent runtime.

## Windows installation

From the checkout in PowerShell:

```powershell
py -3 -m venv "$HOME\.venvs\universal-qa-agent"
& "$HOME\.venvs\universal-qa-agent\Scripts\python.exe" -m pip install -r requirements-core.txt
```

Use the full environment interpreter to select your agent:

```powershell
& "$HOME\.venvs\universal-qa-agent\Scripts\python.exe" scripts/install_agent_skills.py --agent codex
& "$HOME\.venvs\universal-qa-agent\Scripts\python.exe" scripts/install_agent_skills.py --agent claude
& "$HOME\.venvs\universal-qa-agent\Scripts\python.exe" scripts/install_agent_skills.py --agent copilot
```

Run only the commands for the agents you want. Ask your coding agent to use that same full interpreter path for helper commands. The installer tries directory symlinks and uses Windows junctions if symlink creation is unavailable. Quote paths containing spaces.

## Codex plugin

Register the GitHub marketplace:

```sh
codex plugin marketplace add RavenGeeVee/universal-qa-agent
```

Restart the ChatGPT desktop app. In the Plugins Directory, choose **Universal QA Local** and install **universal-qa-agent**. Start a fresh Codex conversation in the target repository and select the plugin's onboarding skill. Use the exact name shown in the skill picker, including a namespace if displayed.

The catalog identifier is `universal-qa-local`; its source package is `plugins/universal-qa-agent`. Marketplace registration and plugin installation are separate steps. See the [official Codex marketplace guidance](https://developers.openai.com/plugins/build/plugins#add-a-marketplace-from-the-cli).

For a source checkout used in plugin development, you can register a local marketplace instead:

```sh
codex plugin marketplace add /absolute/path/to/universal-qa-agent
```

Use the GitHub registration for Git-backed updates. Client availability and organization settings can affect plugin discovery.

## Personal skills

From an activated Python environment in the source checkout:

| Agent | Command | Personal destination |
| --- | --- | --- |
| Codex | `python3 scripts/install_agent_skills.py --agent codex` | `~/.agents/skills` |
| Claude Code | `python3 scripts/install_agent_skills.py --agent claude` | `~/.claude/skills` |
| GitHub Copilot | `python3 scripts/install_agent_skills.py --agent copilot` | `~/.copilot/skills` |

No `--agent` flag selects Claude Code and GitHub Copilot together. The installer preflights selected destinations and refuses unrelated occupied paths. Use one Codex installation method to avoid duplicate plugin and standalone skills. Copilot also recognizes some shared skill locations, so check for duplicate entries when installing multiple local agents.

Start a fresh session after installation. In Codex, invoke `$qa-onboard-repo` and then `$jira-test-generator QA-123`. In Claude Code, invoke `/qa-onboard-repo` and then `/jira-test-generator QA-123`. In a supported local Copilot client, request the skill by name in agent chat. The [README](../README.md) has full prompt examples.

These commands install personal skills on your local machine. Cloud sessions run in separate environments and need their own source resources, Python environment, and profile-store access.

## First use in each repository

1. Open the target automation repository in your selected agent. Tell it which Python environment to use.
2. Invoke `qa-onboard-repo`. The agent inspects code and configuration, then presents repository identity, framework, conventions, reusable patterns, evidence, and open questions.
3. Review the draft. After your explicit approval, the helper validates it and writes a content-bound approval record.
4. Invoke `jira-test-generator` with an issue key. Supply issue content if Jira retrieval is unavailable.
5. Review requirements, traceable cases, existing coverage, proposed files, and command scopes. Approve implementation before target edits.
6. Approve the exact argument vector and working directory before verification runs. Review actual results and unresolved gaps afterward.

The profile helper performs deterministic checks. The coding agent uses its own model and tools for analysis, planning, and code changes. Profile-store writes, target edits, commands, and Jira access remain subject to the active host's permissions.

## Shared profiles across agents

Profiles default to `~/.local/share/universal-qa-agent/repo-profiles`, including on Windows, where Python expands `~` to the user home directory. Each profile directory is keyed by repository identity and target scope. Approved records bind `profile.yaml`, `conventions.md`, and `patterns.md` to the accepted contents.

Git identity uses `origin` when present, or the only configured remote. If several remotes exist without `origin`, select one explicitly with `--remote`. Monorepo subdirectories have separate scopes. Without a usable remote the helper uses the canonical filesystem path. Different SSH host aliases can produce different normalized identities; keep the defining remote consistent when sharing a profile across checkouts.

To use a custom store, export an absolute path before launching the agent.

macOS/Linux:

```sh
export UQA_PROFILES_DIR="$HOME/qa-agent-profiles"
```

Windows PowerShell:

```powershell
$env:UQA_PROFILES_DIR = "$HOME\qa-agent-profiles"
```

Set the same value in every agent process that should share the store. Desktop apps launched separately may need the setting supplied through their own environment or helper arguments. The helper accepts `--profiles-dir` before a subcommand; relative store paths are rejected.

From the source checkout, examples using the configured Python environment are:

```sh
python3 scripts/qa_agent.py profiles
python3 scripts/qa_agent.py profile-path --repo /absolute/path/to/target
python3 scripts/qa_agent.py profile --repo /absolute/path/to/target
python3 scripts/qa_agent.py --profiles-dir /absolute/profile-store profiles
```

`profile-path` prints a destination without creating it. The onboarding workflow creates drafts; `approve-profile --repo <target> --approval-reference "<approval note>"` is used only after the user has reviewed and explicitly approved the profile. Keep private knowledge out of the plugin package.

## Updates

For a Git-backed Codex marketplace:

```sh
codex plugin marketplace upgrade universal-qa-local
```

Refresh/reinstall the plugin in the desktop interface as appropriate and start a new conversation. The host can load a cached installation rather than your source checkout.

For personal skills, update the source checkout and its Python environment:

```sh
git pull --ff-only
python3 -m pip install -r requirements-core.txt
```

The links continue to use the same source path. If you move the checkout, inspect the existing link destinations and reinstall from the new location; do not overwrite unrelated skills. Profiles are held separately from the source and release package.

## Troubleshooting

| Symptom | Action |
| --- | --- |
| Marketplace is not configured as a Git marketplace | Register the GitHub source instead of a local folder: remove the `universal-qa-local` registration, then run the GitHub `marketplace add` command. This changes the catalog registration, not saved QA profiles. |
| Skill does not appear | Start a fresh session, inspect the relevant personal skills directory or enabled plugin, and confirm the client supports that skill location. Check organization policy and duplicate skill names. |
| Installer refuses an existing destination | Inspect whether it belongs to this checkout or another skill. Resolve the conflict explicitly; the installer preserves unrelated paths. |
| YAML/schema dependency error | Use the prepared environment's Python and install its requirements. Confirm the agent uses that interpreter, not the system interpreter. |
| Profile store access denied | Grant scoped access to the configured store or select an approved absolute location. Keep the store consistent across agents. |
| Profile is missing or cannot be loaded | Onboard the exact repository identity/scope and review the reported validation or approval mismatch before proceeding. |
| Jira cannot be retrieved | Connect an available Jira integration or supply the issue description and acceptance criteria. |

## Release maintenance

Root `skills/`, `schemas/`, `scripts/qa_agent.py`, `requirements-core.txt`, `repo-profiles/template/`, and `plugin.json` are the canonical package sources. The clean release at `plugins/universal-qa-agent` is included in Git with `.agents/plugins/marketplace.json`.

Refresh the release with `python3 scripts/package_plugin.py` after obtaining approval for that exact packaging command. The packager includes only public resources and refuses to overwrite an existing package. Preserve or explicitly remove the previous release directory before rebuilding, then commit the refreshed release alongside the source changes. Personal links use the root sources; Codex marketplace installations use the packaged copy.

## Verification policy

Builds, tests, lint, formatting, and validation commands require approval for the exact command before execution. The test command is documented in [tests/README.md](../tests/README.md). Keep command completion, passing tests, and live host workflow verification distinct in reports.
