Repository layout flattened (2026-01-13)
=====================================

Summary
-------
The repository layout was flattened to simplify imports and development. Notable changes:

- Top-level `src/` now contains code previously under nested component folders (chronicle-keeper, narrative-engine).
- Tests moved to the top-level `tests/` directory.
- A root virtual environment `./venv` and a consolidated `requirements.txt` were added for local development.

Why
---
- Reduces PYTHONPATH confusion during test runs and local development.
- Simplifies packaging and CI configuration.

Notes & Next Steps
------------------
- Update any external tooling or deployment scripts that referenced the old nested paths.
- The agent updated `AGENTS.md` with venv usage instructions and added this summary file.
