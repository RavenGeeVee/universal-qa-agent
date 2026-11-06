# Universal QA Agent

Turn Jira requirements into automated tests that follow your repository's existing conventions. Universal QA Agent works with **Codex**, **Claude Code**, and **GitHub Copilot** using two shared workflows:

- **qa-onboard-repo** inspects an automation repository and creates an evidence-backed profile of its framework, structure, conventions, and reusable patterns.
- **jira-test-generator** analyzes a Jira issue, maps requirements to scenarios, identifies coverage gaps, and implements the changes you approve.

Each coding agent supplies its own model and tools. The local Python helper handles repository identity, profile approval, and artifact validation. Jira access comes from the connection available in your agent session, or from issue content you provide.

## Choose your installation

| Agent | Installation | Where it is available |
| --- | --- | --- |
| Codex plugin | Register the GitHub marketplace, then install through the desktop Plugins Directory | Local Codex sessions where the plugin is enabled |
| Codex standalone skills | `python3 scripts/install_agent_skills.py --agent codex` | Personal skills under `~/.agents/skills` |
| Claude Code | `python3 scripts/install_agent_skills.py --agent claude` | Personal skills under `~/.claude/skills` |
| GitHub Copilot | `python3 scripts/install_agent_skills.py --agent copilot` | Local Copilot surfaces supporting personal skills under `~/.copilot/skills` |

Install once per machine and use the workflows across your automation repositories. Choose either the Codex plugin or Codex standalone skills to avoid duplicate entries. Personal skill links require keeping this checkout at a stable location. Local home-directory links do not provision cloud agent environments.

## Prerequisites and Python setup

Install Git, Python **3.10 or newer**, and the coding agent you want to use. Your agent needs access to the target repository, the profile store, and the Python helper. For ticket retrieval, connect Jira through the agent's supported integration; otherwise provide the issue description and acceptance criteria.

Clone the project into a stable directory:

```sh
git clone https://github.com/RavenGeeVee/universal-qa-agent.git
cd universal-qa-agent
```

On macOS/Linux, create a dedicated Python environment and install the helper dependencies:

```sh
python3 -m venv ~/.venvs/universal-qa-agent
source ~/.venvs/universal-qa-agent/bin/activate
python3 -m pip install -r requirements-core.txt
```

On Windows PowerShell:

```powershell
py -3 -m venv "$HOME\.venvs\universal-qa-agent"
& "$HOME\.venvs\universal-qa-agent\Scripts\python.exe" -m pip install -r requirements-core.txt
```

The dependencies are PyYAML and jsonschema. Use this environment's Python when the agent runs the helper. A desktop app or an already-open editor may not inherit your terminal environment: tell the agent the full interpreter path if necessary. See [Python environment setup](docs/local-development.md#python-environment) for commands and examples.

Commands below use standard tool names; RTK users can prefix supported commands with `rtk`.

## Codex plugin installation

Register the repository marketplace:

```sh
codex plugin marketplace add RavenGeeVee/universal-qa-agent
```

Restart the ChatGPT desktop app, open **Plugins Directory**, select **Universal QA Local**, and install **universal-qa-agent**. The marketplace identifier is `universal-qa-local`. Registration makes the catalog discoverable; installation enables the plugin. This uses the [Codex marketplace workflow](https://developers.openai.com/plugins/build/plugins#add-a-marketplace-from-the-cli).

Open a target automation repository in a fresh Codex conversation. Select the plugin's `qa-onboard-repo` skill using the name displayed in the skill picker; plugin skills can have a namespace. Ask:

```text
Use Universal QA Agent to onboard this repository.
Show the profile, evidence, reusable patterns, and any questions for review.
Do not run builds or tests.
```

After reviewing and approving the profile, select `jira-test-generator` and supply a Jira key:

```text
Use Universal QA Agent to analyze QA-123 for this repository.
Show requirements, scenarios, existing coverage, and the proposed change plan.
Wait for my approval before editing code or running verification commands.
```

The plugin includes its helper, schemas, template, and `requirements-core.txt`. The Python environment prepared above supplies the same helper dependencies; installing the plugin itself does not install Python packages.

## Codex standalone skill installation

From the Universal QA Agent checkout:

```sh
python3 scripts/install_agent_skills.py --agent codex
```

Open Codex in your target repository, start a fresh conversation, and invoke:

```text
$qa-onboard-repo
```

After profile approval:

```text
$jira-test-generator QA-123
```

Use the prepared Python interpreter for helper commands. On Windows, invoke the installer with the environment's `python.exe` as shown in the [detailed guide](docs/local-development.md#windows-installation).

## Claude Code installation

From the Universal QA Agent checkout:

```sh
python3 scripts/install_agent_skills.py --agent claude
```

Open your target repository in Claude Code and start a fresh session. Invoke:

```text
/qa-onboard-repo
```

Review and approve the profile, then invoke:

```text
/jira-test-generator QA-123
```

The skills are personal to your machine and available across projects through Claude Code's [personal skill location](https://code.claude.com/docs/en/skills). Jira and repository permissions come from the active Claude Code session.

## GitHub Copilot installation

From the Universal QA Agent checkout:

```sh
python3 scripts/install_agent_skills.py --agent copilot
```

Open the target repository in a local Copilot client supporting Agent Skills, such as VS Code agent mode or Copilot CLI. Start a new agent conversation and ask:

```text
Use the qa-onboard-repo skill to inspect this automation repository
and prepare its profile for review. Do not run builds or tests.
```

After approval, ask:

```text
Use the jira-test-generator skill for QA-123.
Prepare scenarios and an automation plan using the approved repository profile.
Wait for my approval before changing files or running verification commands.
```

Copilot selects skills from their names and descriptions. The installer uses GitHub's supported [personal skills directory](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills). Its availability depends on the local client and organization settings.

To install both Claude Code and Copilot skills together, run the installer without `--agent`:

```sh
python3 scripts/install_agent_skills.py
```

## How the workflow runs

```text
Target repository → onboarding → profile review and approval
                                           ↓
Jira issue → requirement analysis → scenarios → coverage comparison
                                           ↓
                              change plan → your approval
                                           ↓
                              generated changes → approved verification
```

Onboarding inspects the target without editing its code. The profile records the framework, source layout, reusable patterns, evidence, and knowledge gaps. The helper validates its schema and binds approval to the exact profile, conventions, and patterns contents.

For Jira work, the agent connects each scenario to its requirements, compares it with existing automation, and proposes reuse, extension, creation, or a blocked decision. You review target paths, assumptions, and command scopes before implementation. The final report includes traceability, changed files, actual verification results, and unresolved gaps.

The agent requests approval for profile acceptance, target edits, exact verification commands, and knowledge updates. Tool-level enforcement depends on the host's permission configuration; conversational approval alone is not a technical gate.

## Use across repositories and agents

Open each target repository in your chosen agent and onboard it. Profiles are shared locally under:

```text
~/.local/share/universal-qa-agent/repo-profiles/repo-<identity-digest>/
```

Identity uses a normalized Git remote and target subpath, or a canonical filesystem path when no usable remote exists. Monorepo subprojects have separate scopes. Agents on the same machine can use the same approved profile when they resolve the same identity and profile store.

Set `UQA_PROFILES_DIR` to an absolute path to choose another store, and make it available to each agent process. Profiles stay outside the plugin installation and target repository. For remote selection, environment configuration, and helper commands, see [the setup guide](docs/local-development.md).

## Updates

For the Codex GitHub marketplace:

```sh
codex plugin marketplace upgrade universal-qa-local
```

Refresh the installed plugin through the desktop interface and start a new conversation. For personal skill links, update the source checkout and restart the agent session:

```sh
git pull --ff-only
python3 -m pip install -r requirements-core.txt
```

Run the install command again if the checkout location changes. The installer refuses unrelated occupied skill paths and supports Windows junctions when symbolic links are unavailable.

## Project structure

| Location | Purpose |
| --- | --- |
| `skills/` | Shared onboarding and Jira automation workflows |
| `scripts/qa_agent.py` | Identity-scoped profiles, local schema/cross-artifact validation, and content-bound approval |
| `scripts/install_agent_skills.py` | Personal skill installation for each supported agent |
| `schemas/` | Profile, requirement analysis, test case, plan, knowledge proposal, and validation result contracts |
| `repo-profiles/template/` | Empty repository profile template |
| `plugins/universal-qa-agent/` | Clean Codex release package distributed through GitHub |
| `.agents/plugins/marketplace.json` | Marketplace catalog referencing the release package |
| `agent-adapters/` | Host-specific setup and capability boundaries |
| `core/` | Portable workflow and contract design |
| `tests/` | Helper, installation, packaging, and release consistency tests |

The coding agent performs analysis, scenario design, and code editing; deterministic checks run in the Python helper. Contributors edit the root sources and refresh the release package before publishing. Packaging and repository verification follow the exact-command approval policy; see [release maintenance](docs/local-development.md#release-maintenance).

## Further documentation

- [Installation, Python environments, updates, and troubleshooting](docs/local-development.md)
- [Repository onboarding](docs/repository-onboarding.md)
- [Jira-to-automation workflow](docs/jira-automation.md)
- [Knowledge maintenance](docs/knowledge-maintenance.md)
- [Identity, validation, capabilities, and approval controls](docs/p0-design-controls.md)
- [Test commands and coverage](tests/README.md)
