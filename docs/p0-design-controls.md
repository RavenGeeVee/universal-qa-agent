# P0 design controls

This document defines the cross-agent behavior required before the Universal QA Agent is treated as safe for routine Jira-to-test generation. The JSON Schemas under `schemas/` are the portable data contracts; adapters translate host capabilities and human approval into those contracts.

## 1. Repository identity and profile resolution

- Prefer the `origin` remote. If `origin` is absent and there is exactly one remote, use that remote; if several remotes exist without `origin`, ask which one defines repository identity. Strip embedded credentials, query strings, and fragments; lowercase the host, convert supported SSH and HTTPS URL forms to the same host/path form, and remove a trailing `.git`. Preserve repository path case. Unsupported remote forms fall back to canonical filesystem identity rather than guessed normalization.
- Without a usable remote, use the canonical filesystem root as a local-only identity. Do not infer identity from a folder name.
- Include the target's relative path from the Git root as `scope` (`.` for a whole repository). Calculate the profile key as `sha256(UTF-8(kind + NUL + normalized_value + NUL + scope))`. Store profiles under a Windows-safe directory named `repo-<64 lowercase hex digest>`; store the prefixed `sha256:<digest>` in the profile contract. Retain the folder name and local root only as display/current-checkout metadata.
- Require exactly one identity match. Missing, duplicate, malformed, or mismatched identity blocks profile loading and triggers an explicit resolution request.
- Schema 1.0 profiles lack the identity contract. Treat them as migration drafts: inspect and bind them to a verified identity, validate them, then require approval before making them loadable. Never silently migrate or overwrite accepted knowledge; preserve the old profile and write the migrated draft to its identity-keyed directory.

The repository profile schema is version 1.2 and requires scoped identity fields. The helper resolves profiles by the derived identity key, not the folder name.

## 2. Scoped approval across hosts

Use separate approvals for separate effects:

- **Profile approval:** accept an onboarding or profile update for one repository identity.
- **Target edit approval:** approve the presented plan and affected target paths before writing target automation.
- **Command approval:** approve the exact executable, arguments, and working directory before a build, test, lint, formatting, or validation command runs.
- **Knowledge approval:** approve a named repository-specific or universal knowledge change before it is saved.

An approval is valid only for the exact displayed plan or knowledge proposal. A changed plan, added target file, modified command, or changed knowledge proposal needs a new approval. Validation-command scopes contain the exact argument vector and working directory. The adapter binds approval to SHA-256 of canonical UTF-8 JSON (keys sorted, no insignificant whitespace). For a plan, the payload includes `schema_version`, `issue_key`, `items`, `approval_required`, `scopes`, and `unresolved_gaps`; for a knowledge proposal it includes all proposal fields except `approval`. The helper verifies the digest; the adapter obtains a human decision and records its reference; the model cannot approve on the user's behalf.

Each adapter reports Jira read, repository read/write, profile-store write, command execution, target-write gate, and command gate separately. `available` means the host blocks the action until approval; `unavailable` means only a conversational approval prompt is available; `unknown` is treated as unavailable. If the host cannot enforce a gate, the skill must stop before the action, ask for explicit user approval, and report that enforcement is instruction-level. The cross-agent design does not claim that instructions or JSON fields alone can prevent a host from performing an action.

## 3. Deterministic artifact validation

Validate each generated JSON artifact against its versioned schema before it is treated as ready. Resolve only local references:

1. Repository profile before it can receive the accepted-profile marker.
2. Requirement analysis and test cases before the automation plan is prepared.
3. Automation plan before approval is requested.
4. Knowledge proposal before review and persistence.

Use a local Draft 2020-12 JSON Schema validator with format checking and a safe YAML parser for `profile.yaml`. Validation does not fetch remote schemas or execute YAML tags. In addition to schema structure, run deterministic cross-artifact checks: recompute repository identity keys during profile loading, require unique requirement and acceptance-criteria IDs with source evidence, ensure every test case references existing IDs, ensure each automation-plan item references an existing test-case ID, bind approval digests to the plan/proposal including schema version, and compare command/target scopes with their referenced contracts. Universal knowledge needs evidence from at least two repository identities. Invalid output, unsupported schema versions, and unavailable validation block the next stage. A human/model review can add judgment but cannot replace schema validation. Repository build and test commands remain a distinct, approval-gated validation stage.

The local helper uses `requirements-core.txt` for PyYAML and jsonschema. Install these dependencies locally before using schema validation; no hosted service or LLM API is used.

## 4. Jira and host capability reporting

Before analysis, the adapter reports availability and limitations for Jira read, repository read, repository write, profile-store write, command execution, target-write gate, and command gate. Jira analysis records whether content was retrieved, supplied by the user, partial, or unavailable; it lists missing sources and retrieval limits. The helper rejects status/source contradictions. Do not describe linked issues, comments, or acceptance criteria as retrieved unless the host actually supplied them.

Treat `unknown` as unavailable for claims and consequential actions. If Jira is unavailable or unknown, use only issue content supplied by the user and mark the source accordingly. If repository read access is unavailable or unknown, do not propose repository-specific reuse or claim a completed gap analysis. If write or command capabilities are unavailable or unknown, stop before those phases and report them as blocked until the capability or approval is established.

## Acceptance criteria for runtime implementation

- Two repositories with the same folder name resolve to distinct identities and never load each other's profiles.
- Two checkouts with the same normalized Git remote resolve to one profile; an unversioned/local-only checkout uses a path identity.
- A stale, malformed, duplicated, or legacy profile cannot be loaded without identity resolution and explicit migration approval.
- Every generated contract artifact is schema-validated; invalid output fails closed with actionable paths/codes.
- Cross-artifact references and approval digests are checked deterministically.
- A plan cannot authorize a different file or command than the user approved.
- Capability and Jira-source limitations appear in the generated report and traceability data.
- Each host adapter states whether approvals are technically gated; unsupported gating stops the action pending direct user approval.
