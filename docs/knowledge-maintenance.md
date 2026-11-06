# Knowledge maintenance

For each discovery, record the statement, classification (universal or repository-specific), supporting evidence, affected knowledge file, repository identity when applicable, and confidence/uncertainty. Check existing instructions and profiles for duplication or conflict before proposing a change. Validate the proposal against `schemas/knowledge-proposal.schema.json` and show the exact proposed scope before requesting approval.

- Repository-specific facts belong only in that repository's profile and references.
- Cross-repository workflow rules may be proposed for universal core documentation only when evidence supports generalization.
- Preserve useful examples with source provenance; do not copy secrets or sensitive test data.
- Present updates as a diff or equivalent reviewable proposal. Do not persist accepted profile or shared-knowledge changes without explicit approval scoped to the named identity and knowledge files.
- If the deterministic validator is unavailable, keep the proposal unvalidated and do not persist it.
- After approval, update the appropriate file and report the change. On conflict, keep the prior accepted rule and surface the conflict for resolution.
