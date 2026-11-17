# Publishing Universal QA Agent

The distributable plugin is `plugins/universal-qa-agent`. Codex and Claude Code install the same two skills, helper, schemas, and empty profile template. Their repository catalogs both use the stable marketplace identifier `universal-qa-local`; that identifier does not mean the repository must be private or local-only.

Version `0.1.5` is the prepared release version. Source preparation, successful validation, a GitHub release, and acceptance into a public directory are separate milestones. No directory listing is implied by the files in this repository.

## Release contents and metadata

Before distribution, review these canonical sources and refresh their packaged copies:

| Source | Release purpose |
| --- | --- |
| `plugin.json` | Portable identity, publisher links, and OpenAI presentation metadata |
| `.claude-plugin/plugin.json` | Claude Code identity and publisher metadata |
| `docs/plugin-readme.md` | Standalone `README.md` inside the plugin package |
| `LICENSE` | MIT license included with the distributed plugin |
| `assets/` | Bundled display artwork |
| `skills/`, `schemas/`, `scripts/qa_agent.py` | Workflow instructions and local helper |
| `requirements-core.txt`, `repo-profiles/template/` | Helper dependencies and empty profile template |
| `.agents/plugins/marketplace.json` | Codex catalog pointing to the release folder |
| `.claude-plugin/marketplace.json` | Claude Code catalog pointing to the same release folder |

Keep the plugin name and marketplace identifier stable. Use the same version in both source manifests and both packaged manifests. Increment it for each published update. Review the publisher identity, repository and support links, descriptions, artwork, and [data-handling notice](privacy.md). Public URLs must resolve after the changes are pushed. The project uses the MIT license; include `LICENSE` in the plugin folder and ZIP. Anthropic's [pre-submission checklist](https://claude.com/docs/plugins/pre-submission-checklist) checks the packaged README and license as well as the plugin layout.

Profiles, approval records, saved feedback, credentials, conversations, target repositories, developer configuration, and generated verification results do not belong in the release. Preserve the source checkout's private `repo-profiles` data when preparing a release.

## Prepare and review the release

The packager refuses to replace an existing release directory or archive. Preserve the existing `plugins/universal-qa-agent` directory outside the checkout under an agreed unused temporary path before rebuilding; do not delete private profile stores. Review that move as a separate local action.

After approval for this exact packaging command, run it from the source checkout:

```sh
rtk python3 scripts/package_plugin.py --archive
```

It creates the release folder and `dist/universal-qa-agent-0.1.5.zip`. The ZIP opens directly into the plugin files: `plugin.json`, `.claude-plugin/`, `skills/`, and the remaining public resources, without a wrapper directory. `dist/` is ignored by Git; the clean release folder is committed.

This repository requires approval for every exact verification command. The following are proposed release checks, not a record that they have run:

```sh
rtk python3 -m unittest discover -s tests -v
rtk claude plugin validate --strict ./plugins/universal-qa-agent
rtk claude plugin validate .
```

Review the source and packaged diffs for unintended files and private information. Then perform a clean installation in each intended host with an explicit profile store, the prepared Python environment, and a synthetic repository/ticket. Confirm onboarding, profile approval and reload, Jira planning, project-template or CSV output, write approval, and the requirement to approve exact verification commands. Registration or manifest validation alone does not demonstrate that the workflows run successfully.

For a local Claude Code installation, review and authorize these configuration-changing commands separately:

```sh
rtk claude plugin marketplace add .
rtk claude plugin install universal-qa-agent@universal-qa-local
```

Use the [installation guide](../README.md) for Codex registration and desktop installation. Avoid conflicting local and Git registrations with the same marketplace identifier. Preserve existing host configuration and local profiles.

## Publish the repository release

After the checks pass and the release diff is approved:

1. Commit the public source changes, both catalogs, and refreshed `plugins/universal-qa-agent` folder. Include the required `Co-authored-by: Codex <noreply@openai.com>` trailer for a Codex-created commit.
2. Push the reviewed commit to the intended branch with explicit authorization.
3. Optionally tag that commit as `v0.1.5` and attach the generated ZIP to a GitHub release. Confirm the tag and release destination before publishing.
4. From a clean host setup, install from `RavenGeeVee/universal-qa-agent` using the [documented commands](../README.md#choose-your-installation). Check that it fetches the committed release rather than a development copy.

Once pushed to an accessible repository, the catalogs provide direct GitHub distribution. That does not automatically put the plugin in either vendor's public directory.

## Submit for the OpenAI directory

Use the [OpenAI plugin portal](https://platform.openai.com/plugins) and follow the [submission guide](https://developers.openai.com/plugins/deploy/submission). Prepare the publisher's verified developer identity and submission permissions. Upload the plugin ZIP, review metadata and skill findings, resolve required issues, and submit for review. Publish only after approval and your final release decision.

This plugin uses local Git, Python, repository files, and a writable profile store. Its OpenAI metadata declares `requires_local_executor: true`, following the [desktop-only skills guidance](https://developers.openai.com/plugins/deploy/desktop-only#plugins-without-an-mcp-server). It supplies no MCP server. Describe the local runtime requirements and host-provided Jira connection accurately; do not advertise browser-only operation. Package or skill updates require a new ZIP.

## Submit for Anthropic's directory

Open the [Anthropic developer portal](https://claude.ai/directory/manage) and use the [plugin submission guide](https://claude.com/docs/plugins/submit). Enter:

| Portal field | Value |
| --- | --- |
| Repository | `RavenGeeVee/universal-qa-agent` |
| Plugin path | `plugins/universal-qa-agent` |
| Branch or tag | The reviewed release branch or tag |

Use an eligible account with its GitHub connection authorized to push to the repository. Supply a real contact address in the portal. Run portal validation on the final commit, resolve findings, review the listing and data-handling answers, then submit. Complete the portal's review and publish steps; passing a check alone does not make the plugin live.

The directory reads the selected plugin folder. Its local helper requires repository and filesystem access, so confirm support on each surface you intend to list. Anthropic's directory and the `claude-plugins-official` marketplace have different publication routes; the latter is a partner-contact route, as explained in [Claude Code's publishing documentation](https://code.claude.com/docs/en/plugins/publish#submit-to-anthropics-directory).
