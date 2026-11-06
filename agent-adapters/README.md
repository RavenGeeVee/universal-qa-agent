# Agent adapters

An adapter maps a host's tools and instructions to the shared workflows: declare available Jira/repository/editing/command capabilities, preserve requirement sources and repository evidence, present approval-gated plans, and report changed files, traceability, results, and gaps.

The canonical workflows live once in root `skills/`. Codex uses the skills-only plugin; Claude Code and GitHub Copilot use personal Agent Skills links installed by `scripts/install_agent_skills.py`. Persistent target knowledge lives outside the installed package. See [local setup](../docs/local-development.md).

Host-specific integrations stay thin and must keep shared schemas and project knowledge separate from vendor APIs. Each adapter reports Jira, repository, profile-store, command, target-write-gate, and command-gate capabilities. It requests scoped human approval before target writes, exact validation commands, and knowledge persistence. A conversational skill cannot enforce a technical gate when the host exposes unrestricted write or command tools; it must stop immediately before those actions and report that limit. Jira retrieval and repository editing depend on each active host's available tools and permissions.
