# Universal core boundary

The core owns workflow decisions and portable contracts, not host-specific APIs. Its future implementation must expose these conceptual operations:

- `identify_repository(root) -> repository_identity`
- `resolve_profile(identity) -> exactly_one_profile | missing | ambiguous`
- `analyze_requirements(issue_context, host_capabilities) -> requirement_analysis`
- `design_test_cases(requirement_analysis, profile) -> test_cases`
- `analyze_gaps(test_cases, repository_inventory, profile) -> automation_plan`
- `request_approval(scope) -> approval_record`
- `propose_knowledge_update(discovery, current_knowledge) -> knowledge_proposal`
- `validate_artifact(artifact, schema, related_artifacts) -> validation_result`

`identify_repository` uses `origin`, or the only configured remote if there is exactly one; multiple remotes without `origin` require user selection. It produces a normalized identity from that credential-free remote when available, otherwise from the canonical filesystem root. The profile key is SHA-256 of UTF-8 `kind + NUL + normalized_value`; store paths use `repo-<64 lowercase hex digest>` for Windows compatibility. The display name and local checkout path are metadata, never lookup keys. A miss or multiple matches blocks profile loading until resolved. A schema 1.0 profile without identity requires explicit migration and approval before use.

Inputs must distinguish observed evidence, user-provided requirements, and unresolved inference. Jira retrieval status and host capabilities are part of the requirement-analysis contract; unavailable capabilities and missing issue sections remain visible in the output. Core operations must not silently turn assumptions into requirements or apply knowledge proposals.

## Approval contract

Approval is scoped to an operation and resource: target file edits, an exact validation command and working directory, profile updates, or shared-knowledge updates. Approval applies only to the presented scope; adding files, changing a command, or changing any part of the displayed plan/proposal invalidates it and requires a new approval. The contracts record pending, approved, rejected, or not-required state, an approval digest, and the approved scope reference.

Adapters must report whether their host can enforce approval before writes and command execution. If the host cannot enforce the gate, the workflow must stop before the action and request direct user approval in the conversation. Instructions and schema fields alone are not enforcement.

## Deterministic validation contract

Before an artifact is shown as ready, the core validates it against the versioned JSON Schema contract and runs deterministic cross-artifact checks, then returns the schema path, validity, and structured errors. Checks include identity-key recomputation, globally unique requirement/acceptance-criteria IDs with source evidence, test-case references to those IDs, plan-to-case references, and approval-digest matching. Validate profiles, requirement analyses, test cases, automation plans, and knowledge proposals. Invalid artifacts are blocked from profile acceptance and target-code generation. Validation failure or unavailable validator is a blocking gap; the agent must not silently downgrade to a model-only review. Repository build/test commands are a separate validation phase and still require approval.

## Current implementation boundary

These P0 behaviors are now specified in the schemas and workflow design. The current Python helper still looks up profiles by folder name, does not validate schemas, and does not mediate host file or command tools. The next implementation work must close those runtime gaps before these controls can be claimed as enforced.
