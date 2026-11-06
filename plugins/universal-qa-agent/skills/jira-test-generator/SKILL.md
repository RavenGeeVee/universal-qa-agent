---
name: jira-test-generator
description: Turn a Jira issue into traceable automation scenarios, identify repository coverage gaps, prepare a reviewable plan, and implement approved tests following the current repository's conventions.
---

# Jira to automation

Use the repository open in the active coding agent as the target unless the user provides another path. Explicit user instructions take precedence over this workflow.

## Capability, identity, and validation safeguards

Report Jira read, repository read/write, command execution, and approval-gate capability as available, unavailable, or unknown. Record whether issue content was retrieved, supplied by the user, partial, or unavailable, including missing sources and retrieval limits. Never imply unavailable Jira content was retrieved.

Resolve the accepted profile by schema 1.2 repository identity and monorepo scope, not its folder name. The helper verifies identity, schema, and a content-bound approval record before loading it. Stop on missing, mismatched, ambiguous, or legacy profiles until they are migrated and approved. Validate generated analyses, cases, and plans with the bundled local validator before presenting them as ready.

Resolve this loaded `SKILL.md` to its actual file location (follow symlinks for legacy skill installs). The package root is two directories above its containing skill directory. Resolve bundled `scripts/`, `schemas/`, and `repo-profiles/template/` from that root, never from the target working directory or a fixed clone path. Quote paths when constructing commands. Use Python 3.10 or newer (`python3` on macOS/Linux; `py -3` on Windows).

Profiles live outside the installed package, by default under `~/.local/share/universal-qa-agent/repo-profiles/`. `UQA_PROFILES_DIR` overrides the store with an absolute path; keep this setting consistent across workflows. Use the bundled `scripts/qa_agent.py profile-path --repo <absolute-target-path>` to print the destination. Helpers only read files and print paths. Never store knowledge in the plugin cache or copy agent files into the target. If access is denied, report the required path and request scoped access.

## Inputs and profile

Require a Jira key. Retrieve description, acceptance criteria, comments, and linked issue context only through capabilities actually available in the active session. If Jira is unavailable, ask for the issue content or proceed only with content the user supplied; never claim retrieval that did not happen.

Load the accepted repository profile and its conventions/patterns using:

```sh
<python-3-launcher> "<package-root>/scripts/qa_agent.py" profile --repo "<absolute-target-path>"
```

Use `python3` on macOS/Linux or `py -3` on Windows in place of `<python-3-launcher>`. If no approved profile exists, follow the bundled sibling `../qa-onboard-repo/SKILL.md` workflow before proceeding. The helper verifies that `repository.identity` matches the target; stop on missing identity or any mismatch. Inspect relevant current automation files and profile evidence before proposing changes.

Use the bundled requirement-analysis, test-case, and automation-plan schemas under `schemas/` as output contracts. Include each required `schema_version`. Validate cross-artifact references, retrieval status, target-file scopes, and command scopes against the profile. The plan records pending approval and exact scopes; a command scope contains its argument vector and working directory. Bind approval to the canonical digest of the displayed plan, including schema version. The current adapter cannot mechanically enforce writes or command execution, so stop immediately before those actions and obtain direct user approval.

## Analysis and plan

1. Separate explicit requirements from interpretation. Capture dependencies, ambiguities, and questions.
2. Draft positive, negative, boundary, and relevant regression cases. Give each a stable ID and trace it to requirement/acceptance-criteria IDs. Do not invent expected behavior.
3. Compare each case to existing automation and classify it as reuse, extend, create, or blocked. Cite the target paths and profile patterns that support the choice.
4. Present the plan, target files, assumptions, validation approach, unresolved gaps, and required approval scopes. Stop here unless the user explicitly approves target code changes.

## Approved implementation and validation

After approval, make the smallest changes that fit the repository's conventions. Preserve existing error handling and validation. Do not modify unrelated files.

Before running any build, test, lint, formatting, or other validation command, state its exact argument vector and working directory and wait for user approval. Any command change requires fresh approval. Report actual outcomes and distinguish command success from test success when the repository suppresses failures.

## Knowledge learning

For each new pattern or restriction, check for duplicates and conflicts; classify it as repository-specific or potentially universal; and show a reviewable proposal with evidence. Validate the proposal against `schemas/knowledge-proposal.schema.json`. Keep target-specific facts only in the target profile. Do not update the accepted profile or shared Universal QA instructions until deterministic validation succeeds and the user explicitly approves the exact knowledge scope.

## Final report

Report issue key and available sources, requirement-to-test traceability, gap decisions, files changed, validation command/results, profile updates proposed or approved, and unresolved questions.
