# Local helper tests

`test_qa_agent.py` covers source-checkout profile storage discovery, explicit storage overrides, first-use discovery, approval gating, profile-path CLI behavior, skill installer safety and legacy link migration, plus allowlisted plugin packaging without private profiles or Python caches, using Python's standard-library `unittest` runner. Installer tests also cover the unchanged Claude/Copilot default, explicit agent selection, cross-host preflight safety, and Codex CLI routing.

Package tests check that the Codex and Claude/Copilot marketplace catalogs point to the same release folder, that the portable and Claude manifests share their identity, version, and description, and that both skills are present. They also check that the public release resources match the canonical sources without extra files, that the Claude manifest ships while marketplace metadata and private artifacts stay outside the package, and that the packaging command targets `plugins/`.

Publication tests cover matching publisher and repository metadata, the local-execution declaration, bundled square SVG icons, and the standalone README mapping. Archive tests cover files at the ZIP root, private-profile exclusion, refusal to replace an existing archive, unsafe-version rejection, and the optional archive command route.

Run from the project root only after approving the exact command. On Windows, use `py -3` instead of `python3`.

```sh
python3 -m unittest discover -s tests -p 'test_qa_agent.py'
```

Storage discovery tests cover renamed source checkouts, nested home checkouts, personal skill links outside the home directory, cache/package exclusions, ambiguity, missing sources, and read-only resolution without directory-symlink traversal, including Windows junction/reparse-point exclusion.

Named-profile tests cover repository-name destinations, custom folder labels with unchanged approval records, same-name repository collision protection, duplicate identity rejection, and exclusion of symlinked profile folders. Repository identity remains checked independently of folder labels.

Template-selection acceptance scenarios (manual, subject to command approval): an explicit user template wins; a verified project template preserves custom fields and multi-step layout; conflicting project sources require clarification; unavailable Jira/Zephyr access is disclosed; no verified template selects the bundled CSV; internal case IDs and requirement links match the plan; CSV quoting/formula protection preserves test meaning; no Jira/Zephyr upload occurs without explicit approval. These scenarios describe workflow checks, not automated export tests.

Feedback acceptance scenarios: repository-specific feedback remains a local draft; saving a feedback note leaves profile approval contents unchanged; a shared candidate is sanitized before review; no tool submission happens without an explicit instruction; uncertain findings stay candidates; only a reviewed release changes the shared skill. Packaging exclusion fixtures include private feedback notes; release consistency covers the packaged feedback resources. Workflow acceptance and tests require approval before execution.
