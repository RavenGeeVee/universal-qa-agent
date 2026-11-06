# Install the local plugin

The package uses root `plugin.json` and root `skills/`, following the [official Agent Plugins packaging guide](https://developers.openai.com/plugins/build/plugins). The catalog at `.agents/plugins/marketplace.json` exposes the package as `universal-qa-agent` in the `universal-qa-local` marketplace. Its source is the clean staged package at `dist/universal-qa-agent`; paths resolve from the marketplace repository root.

## Plugin installation

1. Prepare the distributable with `rtk python3 scripts/package_plugin.py` after approving that exact packaging command. It stages the manifest, skills, schemas, profile helper, local dependency declaration, and empty profile template under `dist/universal-qa-agent`. It excludes private drafts, developer settings, and bytecode. It refuses to overwrite an existing output; preserve or explicitly remove that output before rebuilding.
2. Keep this checkout at a stable location. Register its marketplace with `codex plugin marketplace add /absolute/path/to/universal-qa-agent` where supported, or open the repository in the ChatGPT desktop app to discover its repo marketplace.
3. Restart the desktop app, choose **Universal QA Local** in the Plugins Directory, and install **universal-qa-agent**.
4. Start a new Codex conversation in the target automation repository. Select the plugin's onboarding skill, then its Jira generation skill when an approved profile exists. Use the skill names shown by the host; plugin skills may be namespaced.

Availability varies by client. Registering a marketplace is distinct from installing its plugin. This repository change does not register, install, authenticate, or publish anything on your machine.

Distribute only the staged `dist/universal-qa-agent` folder. Git ignores this output; team distribution must arrange for the staged package to be available and point its marketplace at that clean package. No public publication is required for local use. The catalog will not resolve until packaging has been authorized and completed.

When updating the source, rebuild the staged package, then refresh/reinstall the plugin through the host and start a new conversation. The host may execute an installed cache copy rather than this checkout. Keep saved profiles outside the installed package.

## Persistent profile storage

The default on every platform is `~/.local/share/universal-qa-agent/repo-profiles`. Python expands `~` to the user's home directory, including on Windows. Set `UQA_PROFILES_DIR` to a different absolute directory if needed. Relative overrides are rejected to avoid changing storage when the target working directory changes.

The bundled helper resolves resources relative to the loaded skill's actual location, including symlink installs. From this checkout, illustrative commands are:

```sh
python3 scripts/qa_agent.py profiles
python3 scripts/qa_agent.py profile-path --repo /absolute/path/to/target
python3 scripts/qa_agent.py profile --repo /absolute/path/to/target
python3 scripts/qa_agent.py --profiles-dir /absolute/profile-store profiles
```

Use Python 3.10 or newer and install local dependencies with `python3 -m pip install -r requirements-core.txt` (Windows: `py -3 -m pip install -r requirements-core.txt`). `profile-path` prints an identity-keyed destination without creating it. After the user reviews and approves a draft, `approve-profile --approval-reference "<approval note>"` validates it and writes a marker bound to the exact profile contents. Sandbox restrictions may require scoped write approval for the chosen profile location; the workflow must not silently fall back to the plugin cache.

## Existing local profiles

Existing `repo-profiles/<target-name>/` folders stay untouched and are not discovered by the identity-keyed loader. Profile schemas before 1.2 lack scoped identity; treat those profiles as migration drafts. Bind each profile to a verified repository identity, validate the updated schema, and obtain approval before making it loadable. No automatic migration is performed.

Git remotes use `origin`, or the only configured remote. When multiple non-origin remotes exist, pass `--remote` to select one. Monorepo subdirectories have separate profile scopes.

## Personal skill links for Codex, Claude Code, and GitHub Copilot

The two workflows have one canonical source in root `skills/`. From the Universal QA Agent checkout, install personal links with:

```sh
# Default: Claude Code and GitHub Copilot
python3 scripts/install_agent_skills.py

# Or select exactly one host
python3 scripts/install_agent_skills.py --agent claude
python3 scripts/install_agent_skills.py --agent copilot
python3 scripts/install_agent_skills.py --agent codex
```

On Windows, use `py -3 scripts/install_agent_skills.py`. The installer links those workflows to Claude Code (`~/.claude/skills`) and GitHub Copilot (`~/.copilot/skills`); it falls back to Windows junctions and refuses to replace occupied skill paths. The links point back to this checkout, so keep it at a stable location. Codex can use its plugin or standalone links selected with `--agent codex`; avoid enabling both.

Open the target repository in Claude Code and invoke `/qa-onboard-repo`; after reviewing and approving the profile, invoke `/jira-test-generator`. In Copilot, ask it to onboard the current repository or generate automation from a Jira issue; its skill selection is based on each skill's description. Both adapters use the same profile store and approval flow as Codex. Jira retrieval and file/command permissions depend on the active host surface.

Installing personal links modifies the user's home directory; this repository change does not install them automatically.

## Verification

The helper validates schemas and resolves profiles by identity. Tests and live host installation have not been run as part of this change. With explicit approval for the exact command, the helper/package tests can be run from this checkout:

```sh
rtk python3 -m unittest discover -s tests -p 'test_qa_agent.py'
```

Live acceptance also needs a fresh target-project conversation: onboard a draft, approve and load it, plan using supplied issue content or a real Jira connection, confirm edits and commands remain approval-gated, and confirm a plugin refresh preserves saved profiles. Do not run target builds or tests without approval.
