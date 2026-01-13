from datetime import datetime, timezone
from uuid import uuid4
from src.services.event_validator import EventValidator
v = EventValidator()
now = int(datetime.now(timezone.utc).timestamp())
evt = {'id': str(uuid4()), 'type': 'character.move', 'timestamp': now+3600, 'source': 'test_source', 'data': {'character_id': str(uuid4()), 'from_location_id': str(uuid4()), 'to_location_id': str(uuid4())}}
print('now', now)
print('evt_ts', evt['timestamp'])
valid, errors = v.validate(evt)
print('valid', valid)
print('errors', errors)
