# Consolidate `shared_models` into `shared/models`

Summary
-------
The legacy `shared_models` package contained an older `base.py` with serializable
`Model` and `Event` classes. The canonical runtime package is `shared.models`
(used across the codebase and tests). To avoid duplication and import confusion,
we migrated the legacy `base.py` into `shared/models/base.py` and exported the
base classes from `shared.models`.

What changed
------------
- `shared/models/base.py` was added (migrated content from `shared_models/base.py`).
- `shared/models/__init__.py` now exports `Model`, `Event`, and `Serializable`.
- The legacy `shared_models` package can be removed safely.

Status
------
As of 2026-01-13 the shared models consolidation is complete. The following
items were verified and documented:

- `shared/models/base.py` (migrated and exported)
- `shared/models/schemas.py` (canonical pydantic schemas)
- `shared/models/item.py`, `shared/models/character.py`, `shared/models/faction.py` (runtime wrappers with `to_dict`/`from_dict`)
- `shared/models/inventory_service.py` (inventory helpers: add/use/equip/unequip)
- Unit tests under `tests/test_shared_models.py` validate roundtrip serialization and inventory flows.

Run the test suite to confirm everything remains green:

```powershell
$env:PYTHONPATH='src'; .\venv\Scripts\python.exe -m unittest discover -s tests -v
```

Why
---
Keeping a single canonical package for domain models avoids import mistakes,
reduces maintenance overhead, and makes tests and tooling simpler (only one
package to reference).

How to validate
---------------
Run the test suite and ensure imports resolve correctly:

```powershell
$env:PYTHONPATH='src'; .\venv\Scripts\python.exe -m unittest discover -s tests -v
```

If any imports still reference `shared_models`, search and update them to
`shared.models`.

Rollback
--------
If needed, the original files are still present in version control prior to
this change; revert the commit to restore them.
