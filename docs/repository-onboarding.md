# Repository onboarding workflow

1. Resolve a repository identity from a normalized credential-free Git remote and target subpath, or from its canonical root when no remote is available. Show the identity and readable profile path. Reuse the unique existing identity match; otherwise use the target repository directory name. A custom folder label is permitted, but never identify a profile from that label alone. Stop on duplicate identity matches or a name already occupied by another profile.
2. Inventory manifests, directory layout, automation files, test configuration, and declared commands.
3. Inspect representative feature files, tests, step definitions, page objects, helpers, clients, and test data. Record paths and relevant symbols/lines as evidence.
4. Infer language, frameworks, build system, test runner, BDD implementation, structure, naming, reusable patterns, restrictions, and execution commands only when supported by evidence.
5. Draft `profile.yaml`, `conventions.md`, `patterns.md`, and focused examples. Include the identity contract; mark unknown values as unknown or add a knowledge gap; do not guess.
6. Validate the profile against `schemas/repository-profile.schema.json`. Invalid or unvalidated profiles remain drafts and cannot be loaded. Ask for clarification only for gaps that block safe automation.
7. Show evidence, uncertainties, identity, and proposed files for maintainer review. Update the accepted profile only after approval.

For incremental onboarding, inspect new/changed files and reconcile only affected profile claims. Retain evidence for existing claims and flag stale references instead of silently replacing them.
