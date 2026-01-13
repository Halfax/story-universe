from datetime import datetime, timezone
from uuid import uuid4
from src.services.event_validator import EventValidator
now = int(datetime.now(timezone.utc).timestamp())
evt_ts = now + 3600
print('now', now)
print('evt_ts', evt_ts)
print('expr', evt_ts > now + 5)
