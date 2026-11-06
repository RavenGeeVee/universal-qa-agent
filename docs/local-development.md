# Install the local plugin

The package uses root `plugin.json` and root `skills/`, following the [official Agent Plugins packaging guide](https://developers.openai.com/plugins/build/plugins). The catalog at `.agents/plugins/marketplace.json` exposes the package as `universal-qa-agent` in the `universal-qa-local` marketplace. Its source is the clean staged package at `dist/universal-qa-agent`; paths resolve from the marketplace repository root.

## Plugin installation

1. Prepare the distributable with `rtk python3 scripts/package_plugin.py` after approving that exact packaging command. It stages only the manifest, skills, schemas, profile helper, and empty profile template under `dist/universal-qa-agent`. It excludes private drafts, developer settings, and bytecode. It refuses to overwrite an existing output; preserve or explicitly remove that output before rebuilding.
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

Use Python 3.10 or newer. On Windows use `py -3` and quote paths containing spaces. `profile-path` prints a destination without creating it. Only onboarding writes drafts, and only explicit approval permits the `.profile-approved` marker. Sandbox restrictions may require scoped write approval for the chosen profile location; the workflow must not silently fall back to the plugin cache.

## Existing local profiles

Existing `repo-profiles/<target-name>/` folders stay untouched. Profile schema 1.0 has no stable identity; treat those profiles as migration drafts. Bind each profile to a verified repository identity, validate the updated schema, and obtain approval before making it loadable. No automatic migration is performed.

For a temporary transition, set `UQA_PROFILES_DIR` to the absolute legacy checkout's `repo-profiles` directory. This keeps the old location but does not add identity matching. The current helper still selects by folder name; same-named repositories are ambiguous and require manual identity checks.

## Claude Code and GitHub Copilot

The two workflows have one canonical source in root `skills/`. From the Universal QA Agent checkout, install personal links with:

```sh
python3 scripts/install_agent_skills.py
```

On Windows, use `py -3 scripts/install_agent_skills.py`. The installer links those workflows to Claude Code (`~/.claude/skills`) and GitHub Copilot (`~/.copilot/skills`); it falls back to Windows junctions and refuses to replace occupied skill paths. The links point back to this checkout, so keep it at a stable location. Codex continues to use its plugin or the existing Codex-only installer.

Open the target repository in Claude Code and invoke `/qa-onboard-repo`; after reviewing and approving the profile, invoke `/jira-test-generator`. In Copilot, ask it to onboard the current repository or generate automation from a Jira issue; its skill selection is based on each skill's description. Both adapters use the same profile store and approval flow as Codex. Jira retrieval and file/command permissions depend on the active host surface.

Installing personal links modifies the user's home directory; this repository change does not install them automatically.

## Verification

The current helper does not yet validate the new schemas or resolve profiles by identity. Tests and live host installation have not been run as part of packaging. With explicit approval for the exact command, the helper/package tests can be run from this checkout:

```sh
rtk python3 -m unittest discover -s tests -p 'test_qa_agent.py'
```

Live acceptance also needs a fresh target-project conversation: onboard a draft, approve and load it, plan using supplied issue content or a real Jira connection, confirm edits and commands remain approval-gated, and confirm a plugin refresh preserves saved profiles. Do not run target builds or tests without approval.
