# Universal core boundary

The core defines repository identity, portable schemas, workflow decisions, and approval boundaries. Agent-specific APIs live in `agent-adapters/`; repository conventions live in external profiles. The current executable helper handles profile identity, approval records, and local artifact validation. Jira retrieval, scenario design, gap analysis, code editing, and target command execution remain in the shared skills and active host.

See [P0 design controls](../docs/p0-design-controls.md) for the cross-agent contracts, [schemas](../schemas/) for artifact shapes, and [skills](../skills/) for the two user workflows. Keep future core code limited to deterministic behavior shared across adapters.
