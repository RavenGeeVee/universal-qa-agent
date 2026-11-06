# Jira-to-automation workflow

1. Report host capabilities for Jira read, repository read/write, command execution, and approval gating. Retrieve only issue fields actually available; record retrieval status, missing sources, and limits.
2. Produce and validate a requirement analysis: normalized requirements, explicit acceptance criteria, dependencies, ambiguities, questions, and capability status. Separate source facts from interpretation.
3. Draft and validate positive, negative, boundary, and relevant regression cases. Give each case a stable ID and link it to one or more requirement/criterion IDs. Do not invent expected behavior; mark gaps for clarification.
4. Resolve the exact repository profile by identity, inspect current automation and profile patterns, and classify each case as reuse, extend, create, or blocked with repository evidence.
5. Present the validated automation plan, target paths, assumptions, unresolved gaps, and approval scopes before code changes. A plan or skill invocation is not approval.
6. After explicit approval for the displayed target paths, change the smallest set of files consistent with the profile. If the host cannot enforce this gate, stop and request approval immediately before the edit.
7. Before any build, test, lint, formatting, or validation command, present its exact executable, arguments, and working directory and obtain approval. A changed command requires fresh approval.
8. Report requirement-to-test traceability, actual source/capability limits, changed files, validation commands and outcomes, approval scopes, unresolved gaps, and unimplemented cases.

Missing Jira or repository capabilities must be reported explicitly; use only context supplied by the user or host rather than fabricating retrieved data.
