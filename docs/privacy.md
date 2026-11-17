# Privacy and data handling

Universal QA Agent is a set of instructions and a local Python helper. It does not operate a hosted QA service, include telemetry, or automatically send profiles or feedback to its maintainer. Your chosen coding agent and its connected tools process the information used during a workflow under their own account, organization, retention, and privacy settings.

## Information used by the workflows

- Repository onboarding reads source files, repository structure, framework configuration, and Git metadata to identify conventions and reusable patterns.
- Jira analysis uses the issue content you provide or that the active agent retrieves through an available connection. Authorized project-template discovery can read related Jira or Zephyr information.
- The agent can include relevant code, ticket content, profile knowledge, and generated artifacts in its model context. Review your provider's settings and organization rules before using confidential material.

Jira authentication and other service credentials belong to the host's integrations. The plugin does not supply these connections or request that credentials be saved in a profile. Installing Python dependencies, fetching a plugin update, or using a connected tool can contact external services; this plugin does not make the agent session an offline environment.

## Local storage

Approved profile knowledge consists of `profile.yaml`, `conventions.md`, and `patterns.md`. It can contain the repository's name, filesystem root, normalized Git remote or canonical filesystem identity, subproject scope, evidence paths, framework details, and local command conventions. The hidden `.profile-approved` record binds approval to the repository identity and file-content digests. Those digests do not anonymize the profile's other contents.

Profiles live in the discovered source checkout's `repo-profiles` directory or an explicitly selected absolute profile store. The standard checkout store is Git-ignored; a custom store needs its own access controls and exclusions from sharing or synchronization. The release package includes only the empty profile template.

Generated tests are saved only to approved target locations. Planning reports and feedback remain in the conversation unless a save location is agreed. Saved feedback may contain project details and needs the same protection as profiles. Framework logs, reports, screenshots, and traces can also contain sensitive data when verification is authorized.

## Sharing, retention, and deletion

The workflows require explicit approval before publishing to Jira, submitting feedback, or making other external writes. Review the destination and exact content first. Public feedback should use synthetic examples and exclude private repository names, paths, tickets, credentials, profiles, approval records, and raw conversations. See the [feedback workflow](feedback.md).

Local files remain until you delete them; uninstalling a plugin does not delete profiles, generated repository files, reports, or host conversation history. Remove the relevant local files when no longer needed, and use your agent provider's controls for conversations and connected-service records. The maintainer cannot delete data held by those providers or in your own storage.

For a public project question, use the [repository issue tracker](https://github.com/RavenGeeVee/universal-qa-agent/issues) with sanitized details. Do not post private data or credentials there.
