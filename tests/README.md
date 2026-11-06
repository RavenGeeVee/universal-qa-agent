# Local helper tests

`test_qa_agent.py` covers source-checkout profile storage discovery, explicit storage overrides, first-use discovery, approval gating, profile-path CLI behavior, skill installer safety and legacy link migration, plus allowlisted plugin packaging without private profiles or Python caches, using Python's standard-library `unittest` runner. Installer tests also cover the unchanged Claude/Copilot default, explicit agent selection, cross-host preflight safety, and Codex CLI routing.

Package tests also check that the marketplace points to the versioned plugin folder, that its public resources match the canonical sources without extra files, and that the packaging command targets `plugins/`.

Run from the project root only after approving the exact command. On Windows, use `py -3` instead of `python3`.

```sh
python3 -m unittest discover -s tests -p 'test_qa_agent.py'
```

Storage discovery tests cover renamed source checkouts, nested home checkouts, personal skill links outside the home directory, cache/package exclusions, ambiguity, missing sources, and read-only resolution without directory-symlink traversal, including Windows junction/reparse-point exclusion.

Named-profile tests cover repository-name destinations, custom folder labels with unchanged approval records, same-name repository collision protection, duplicate identity rejection, and exclusion of symlinked profile folders. Repository identity remains checked independently of folder labels.
