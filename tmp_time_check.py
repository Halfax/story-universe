from datetime import datetime, timezone
import time
print('datetime.utcnow()', datetime.utcnow(), 'timestamp', datetime.utcnow().timestamp())
print('datetime.now(timezone.utc)', datetime.now(timezone.utc), 'timestamp', datetime.now(timezone.utc).timestamp())
print('time.time()', time.time())
