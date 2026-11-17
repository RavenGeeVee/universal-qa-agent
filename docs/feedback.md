# Feedback and shared improvement

Both QA skills can turn user feedback into a reviewable draft. Repository-specific findings stay in local knowledge; reusable improvements go through an explicitly submitted GitHub issue or PR and maintainer review. Conversations are not collected centrally, and using a skill does not automatically update it for other users.

## Give feedback during a task

After onboarding or Jira automation, describe what worked or what should change:

```text
The generated cases did not preserve this project's test-step layout.
Draft feedback with the observed and expected behavior.
Keep it local and show me a sanitized version before sharing anything.
```

The agent uses the [feedback template](../skills/jira-test-generator/assets/feedback-template.md) to record the skill/version, agent, category, classification, observed behavior, expected outcome, minimal evidence, proposed improvement, and acceptance cases. Reported problems remain labeled as reported unless reproduced. Verification commands still require approval.

## Where feedback goes

| Artifact | Type | Location and approval |
| --- | --- | --- |
| Initial feedback draft | Conversation text or Markdown | Shown locally in the conversation. No automatic file or external submission. |
| Saved local feedback | Markdown (`.md`) | Proposed under `repo-profiles/<repository-name>/feedback/`, respecting the selected profile store and write approvals. This is separate from the three approved profile knowledge files. |
| Repository knowledge proposal | JSON contract plus reviewable change | Uses the existing knowledge-maintenance workflow. Accepted profile changes require approval and renewed content-bound profile approval. |
| Shared issue/PR draft | Sanitized Markdown and, for a PR, proposed source changes | Prepared for user review. Submitting it needs explicit authorization for the destination and exact content. |
| Released improvement | Reviewed skill/resource changes and a versioned plugin package | Maintainer review, permitted verification, approval, and release. Users receive it by updating their installation. |

With a custom profile store, ensure local feedback is excluded from any Git repository or synchronization that would expose it. The standard source-checkout profile store is Git-ignored. If no profile exists yet, agree a local location or keep the draft in the conversation. Never put feedback into a plugin cache.

## Share a reusable finding

1. Separate the general problem from private project details. Use synthetic reproductions where possible.
2. Replace real repository names, paths, remotes, identity keys, ticket identifiers/content, and customer data. Do not attach profiles, approval records, credentials, raw transcripts, or unsanitized logs. Keep feedback local if meaningful sanitization is not possible.
3. Show the sanitized draft and intended destination. The user can submit it manually through the repository's **Issues → New issue → Skill feedback** template, or explicitly authorize an available GitHub tool to submit it. No submission is made by this implementation.
4. Check existing issues before opening a duplicate. Link related feedback and describe differences without exposing local identity data.

Repository-specific preferences are not automatically shared rules. A single reproducible defect can be reported; that report does not itself qualify a discovery as universal knowledge. The existing universal knowledge-proposal requirement for evidence from at least two repository identities still applies. Private identities are not included in public issues.

## Maintainer review and release

Maintainers assess whether a report is reproducible, repository-specific, already covered, conflicting, or broadly useful. Record the decision on the issue/PR rather than silently changing the shared workflow. Repeated independent reports can guide priority; they do not authorize changes on their own.

For an accepted improvement, make the smallest change in the canonical skills/resources and add a meaningful acceptance case or test where needed. Follow the repository's exact-command approval policy for verification. Review the diff for unintended scope and private data, refresh the clean plugin release, and increment its version. A release can refer back to the sanitized issue/PR. Users update their plugin or skill checkout to receive the change; saved local feedback and profiles are not distributed.

The packaged [feedback procedure](../skills/jira-test-generator/references/feedback.md) defines the agent workflow. See [knowledge maintenance](knowledge-maintenance.md) for accepted knowledge updates and [release maintenance](local-development.md#release-maintenance) for packaging.
