# Local helper tests

`test_qa_agent.py` covers persistent profile storage, first-use discovery, approval gating, profile-path CLI behavior, skill installer safety and legacy link migration, plus allowlisted plugin packaging without private profiles or Python caches, using Python's standard-library `unittest` runner.

Run from the project root only after approving the exact command. On Windows, use `py -3` instead of `python3`.

```sh
python3 -m unittest discover -s tests -p 'test_qa_agent.py'
```
