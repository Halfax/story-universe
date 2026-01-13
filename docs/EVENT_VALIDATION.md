# Event Validation

Overview
--------
The `EventValidator` enforces a base event schema, event-type-specific schemas, and
additional semantic rules that cannot be expressed in JSON Schema. It is implemented
at `src/services/event_validator.py` and is used by the chronicle-keeper ingestion
pipeline to reject malformed or semantically invalid events before they reach
continuity and persistence layers.

Key features
------------
- Base schema enforcement: required fields `id`, `type`, `timestamp`, `source`, `data`.
- Event-specific JSON Schemas for known types (e.g. `character.move`, `character.update`, `world.tick`).
- Strict mode: when enabled, unknown event types are rejected.
- Semantic checks: future-timestamp rejection (5s skew tolerance), UUID format checks for `id`, `metadata.causationId`, `metadata.correlationId`, and event-type-specific rules (e.g. `from_location_id != to_location_id`).

API
---
- `EventValidator(strict: bool = True)` — create a validator instance.
- `validate(event: Dict) -> Tuple[bool, List[str]]` — returns `(is_valid, errors)` where `errors` is a list of human-readable messages.
- `EventValidationError` — exception type used for raised validation failures in code paths that prefer exceptions.

Location
--------
- Implementation: [src/services/event_validator.py](src/services/event_validator.py#L1-L400)

Usage example
-------------
```python
from services.event_validator import EventValidator

validator = EventValidator(strict=True)
ok, errors = validator.validate(event_dict)
if not ok:
    # Log or return a clear API error
    raise Exception(f"Invalid event: {errors}")
```

Testing
-------
Unit tests for `EventValidator` live in `tests/test_event_validator.py` and cover base-schema checks, event-specific schema validation, UUID/metadata validation, timestamp checks, and semantic rules.

Extending validation
--------------------
- Add new event type schemas to `EVENT_SCHEMAS` in `src/services/event_validator.py`.
- For semantic checks that require access to database state (e.g. verifying that `character_id` exists), implement a separate validation step that can accept lookup callbacks or a lightweight repository interface — the core validator purposely avoids DB access to keep unit tests fast.

Operational notes
-----------------
- Run the test suite to validate changes:

```powershell
$env:PYTHONPATH='src'; .\venv\Scripts\python.exe -m unittest discover -s tests -v
```

- Toggle strict mode in non-production environments if you need to accept unknown event types for migration or experimentation.

Changelog
---------
- 2026-01-13: Documentation added and EventValidator verified via unit tests.
