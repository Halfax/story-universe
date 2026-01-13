from datetime import datetime, timezone
from uuid import uuid4
from src.services.event_validator import EventValidator
v = EventValidator()
now = int(datetime.now(timezone.utc).timestamp())
evt = {'id': str(uuid4()), 'type': 'character.move', 'timestamp': now+3600, 'source': 'test_source', 'data': {'character_id': str(uuid4()), 'from_location_id': str(uuid4()), 'to_location_id': str(uuid4())}}
errors = []
v._validate_semantics(evt, errors)
print('now', now)
print('evt_ts', evt['timestamp'])
print('errors after _validate_semantics:', errors)
valid, all_errors = v.validate(evt)
print('validate() returned:', valid, all_errors)
