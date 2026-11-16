# Skill artifacts and expected outputs

This reference describes the full Universal QA Agent workflows shared by Codex, Claude Code, and GitHub Copilot. The **agent repository** is the Universal QA Agent source checkout. The **target repository** is the automation project being onboarded or extended.

Onboarding saves repository knowledge in the agent repository's profile store. Jira generation presents structured planning artifacts and, after approval, changes automation files in the target repository. A plan, a generated test, and a passing test run are separate outcomes.

## Repository onboarding: `qa-onboard-repo`

The helper locates the profile store using [the configured discovery order](local-development.md#shared-profiles-across-agents). The default layout is:

```text
universal-qa-agent/
└── repo-profiles/
    └── <repository-name>/
        ├── profile.yaml
        ├── conventions.md
        ├── patterns.md
        └── .profile-approved
```

`<repository-name>` is a placeholder for a local readable label. New folders use the target repository directory name; existing folders are matched by the identity recorded inside the profile. An explicit profile-store override changes the storage root. Real onboarded repository names and paths belong in the developer's local profile store, not shared documentation.

| Artifact | Document type | Contents | When it is saved |
| --- | --- | --- | --- |
| `profile.yaml` | YAML (`.yaml`) | Repository identity and scope, languages, frameworks, source paths, commands, restrictions, evidence, and knowledge gaps. | Created as an onboarding draft; accepted-profile updates require approval. |
| `conventions.md` | Markdown (`.md`) | Naming, package/directory conventions, test organization, and implementation rules supported by repository evidence. | Created with the draft; accepted updates require approval. |
| `patterns.md` | Markdown (`.md`) | Reusable test lifecycle, helpers, fixtures, screen/page objects, data providers, and other observed patterns. | Created with the draft; accepted updates require approval. |
| `.profile-approved` | JSON content in an extensionless hidden file | Identity key, digest of the three knowledge files, explicit approval reference, and approval timestamp. | Written by the helper only after explicit approval and successful validation. |
| Focused examples, when useful | Markdown or repository-native source files | Small examples with source provenance. No fixed example filenames are required. | Optional; stored with the repository knowledge when needed. |

The core reusable knowledge consists of the three YAML/Markdown files. The helper checks their identity, schema, and content-bound approval before loading an accepted profile. The approval record covers those three files; optional example files are not part of that digest. Renaming only the enclosing folder preserves its approved contents. Editing a covered file requires review and renewed approval.

The skill also presents a conversational report with the target path, profile path/status, stack, inspected patterns, evidence, and unanswered questions. There is no required separate onboarding report file.

**Target repository:** onboarding inspects files without creating or modifying target code. It does not install a test framework or run target builds/tests.

## Jira automation: `jira-test-generator`

The skill reads the approved profile and current target code, analyzes the issue, presents a plan, and implements only the approved scope.

### Planning and reporting artifacts

| Artifact | Document type | What users receive | Storage behavior |
| --- | --- | --- | --- |
| Requirement analysis | Structured JSON (`.json`) governed by `requirement-analysis.schema.json` | Requirements, acceptance criteria, dependencies, ambiguities, questions, source/retrieval limits, and host capabilities. | Presented for review; no permanent filename or output directory is prescribed. |
| Test scenarios and requirement links | Verified project template/format, or generic CSV (`.csv`) fallback | The project's case fields and step layout, preserving IDs, preconditions, actions, expected results, test data, and requirement links. | Template source, field mapping, format, and intended save location are shown for review; no permanent directory is prescribed. |
| Coverage analysis | Conversation text/tables, with decisions recorded in the JSON automation plan | Existing test evidence and reuse, extend, create, or blocked decisions. | No separate coverage document is required. |
| Automation plan | Structured JSON (`.json`) governed by `automation-plan.schema.json` | Proposed files, rationale, evidence, unresolved gaps, approval scopes, exact command scopes, and approval digest. | Presented before target edits; no permanent filename or output directory is prescribed. |
| Knowledge-update proposal | Structured JSON (`.json`) governed by `knowledge-proposal.schema.json` | New findings, classification, evidence, affected files, and proposed approval scope. | Conditional on discovering new knowledge; accepted knowledge changes are saved only after approval. |
| Helper validation output | JSON printed to command output | Artifact/schema references, validity, and validation errors. | A retained JSON report exists only if output is explicitly captured. |
| Final execution summary | Conversation text/tables | Sources, requirement-to-test traceability, gap decisions, changed files, commands actually run, outcomes, knowledge changes, and outstanding questions. | No mandatory Markdown, Word, PDF, or other report file is created. |

### Test-case template selection

Use the user's explicit template first. Otherwise, discover the project's established template from approved profile references, repository documents/examples, or authorized Jira/Zephyr project read tools. Preserve its field names, order, step layout, required custom fields, and document format. Record the template source and resolve conflicts instead of assuming a universal Zephyr format. Tool availability depends on the active host session.

When no project template can be verified, use [test-case-template.csv](../skills/jira-test-generator/assets/test-case-template.csv). Its columns are Test Case ID, Jira Issue Key, Requirement IDs, Title, Category, Priority, Preconditions, Step Number, Action, Test Data, Expected Result, and Labels. Use UTF-8, one row per step, repeated case metadata, numbered steps, and semicolon-separated requirement IDs. Unknown optional values stay blank. Standard CSV quoting and spreadsheet formula protection apply. This generic review template is not guaranteed to be directly importable into a project's Zephyr configuration.

The internal `test-case.schema.json` representation supports validation and requirement/plan cross-checks. It does not force a parallel JSON test-case deliverable: users review the selected project document or fallback CSV. Preserve project-specific fields in that document, map core test semantics to the internal representation, and disclose mapping gaps. Other structured artifacts such as requirement analyses and automation plans retain their JSON contracts. The helper validates JSON/YAML inputs, not arbitrary project documents or CSV imports; mapping, spreadsheet protection, and export quality currently rely on the agent workflow.

Reading a project template does not authorize uploading test cases to Jira or Zephyr. Publishing/importing is a separate explicitly approved action.

**Permanent planning storage is not standardized.** Files used as validator inputs can be created during a run, but there is no guaranteed per-ticket directory, filename, archive, or retention policy. If you need lasting planning documents, request the exact artifacts, location, and format as part of the task. Any target-repository writes still need approval.

For example, you can request:

```text
Analyze QA-123 and present the automation plan first.
Also propose a location for retained requirement-analysis.json,
test cases in this project's template (or test-cases.csv as a fallback),
automation-plan.json, and a Markdown summary.
Show the paths for approval before saving them.
Do not change automation code or run verification commands yet.
```

Those filenames are illustrative, not enforced defaults.

### Approved implementation in the target repository

| Artifact | Document/file type | Location and conditions |
| --- | --- | --- |
| New or extended tests | Repository-native source, such as `.java`, `.kt`, `.ts`, `.js`, `.py`, or `.feature` | Existing target test directories, following the approved plan. |
| Required screen/page methods, helpers, fixtures, or test data | Repository-native source or data, such as `.java`, `.ts`, `.json`, `.yaml`, or `.csv` | Existing target structure, only when required for approved cases. |
| Framework test reports | Framework-dependent HTML, XML, JSON, or text logs | Framework-configured output directories, only if an approved command runs and produces them. |
| Screenshots, recordings, and traces | Framework-dependent images, video, or trace archives | Produced only when the target framework/configuration captures them during approved execution. |

No particular source extension, directory structure, screenshot, or report is guaranteed across repositories. The agent reuses the target framework's conventions. Writing automation does not establish that it passed; the final summary must identify what was actually executed.

### Changes in the agent repository

Jira generation normally reads the profile rather than rewriting it. A newly discovered repository convention can result in a proposed update to `profile.yaml`, `conventions.md`, or `patterns.md`; persisting accepted knowledge requires explicit approval and renewed profile approval for changed covered files. Shared workflow changes also require explicit approval. Invoking the skill does not itself authorize knowledge changes.

## Storage and distribution

- Local profiles under the source checkout's `repo-profiles/` are Git-ignored. The distributed plugin includes the empty template, not onboarded repository knowledge.
- Installed plugin caches contain the packaged skills, helper, schemas, and resources; they are not the profile store or a per-ticket report archive.
- Files under `schemas/` are bundled JSON Schema definitions (`.schema.json`), not artifacts generated by each skill run.
- Neither skill automatically commits, pushes, publishes reports, or updates Jira issues. External changes need an explicit request and the relevant host permissions.

See [onboarding](repository-onboarding.md), [Jira automation](jira-automation.md), and [knowledge maintenance](knowledge-maintenance.md) for the workflow and approval rules.
