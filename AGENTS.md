# AGENTS.md

## Scope

* Applies to the full repo.

## Structure & Exports

* Public API lives in flat `util_*.py` modules re-exported via `ubelt/__init__.py`.
* After API changes, run `mkinit ubelt -w` and adjust manually if needed.

## Python, Typing & Docs

* Support Python >=3.8.
* Keep `.py` and `.pyi` in sync; docstring types (Google style) and stubs must agree.
* Inline typing allowed if readability is preserved and no new imports are introduced.

## Tests & Coverage

* Maintain 100% coverage.
* Use `python run_tests.py` (pytest + coverage + xdoctest).
* Use `./run_doctests.sh` for xdoctest-only runs.
* xdoctest (not stdlib doctest) is required.

## Linting & Style

* Follow PEP 8; mark exceptions with `# NOQA`.
* Use Google-style docstrings with runnable examples.

## Dependencies & Packaging

* Requirements in `requirements/*.txt`, dynamically referenced from `setup.py`.
* Keep them synced; migration to full `pyproject.toml` pending.

## Documentation

* Prefer rich docstrings to separate docs.
* Keep `docs/` changes consistent with in-code documentation.

## Notes

* Gradually expand type coverage without breaking compatibility.
* Review `ubelt/__init__.py` ignore/explicit lists when editing platform helpers.
