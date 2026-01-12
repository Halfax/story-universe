
"""
World Clock and Tick Broadcasting for Chronicle Keeper
-----------------------------------------------------
Maintains canonical world time, advances it on a schedule, logs ticks, and (future) broadcasts to Evo-X2.
"""


import threading
import time
from src.db.database import get_connection
from src.messaging.publisher import TickPublisher


def world_clock_loop(tick_interval=5):
	print("[ChronicleKeeper] world_clock_loop thread starting...")
	try:
		publisher = TickPublisher()
		while True:
			conn = get_connection()
			c = conn.cursor()
			# Get current time
			c.execute("SELECT value FROM world_state WHERE key='time'")
			row = c.fetchone()
			current_time = int(row[0]) if row else 0
			new_time = current_time + 1
			# Update time
			c.execute("REPLACE INTO world_state (key, value) VALUES (?, ?)", ("time", str(new_time)))
			# Log tick event
			c.execute("""
				INSERT INTO events (timestamp, type, description, involved_characters, involved_locations, metadata)
				VALUES (?, ?, ?, ?, ?, ?)
			""", (int(time.time()), "system_tick", f"World time advanced to {new_time}", "[]", "[]", "{}"))
			conn.commit()
			conn.close()
			print(f"[PI] World time advanced to {new_time}")
			# Broadcast tick to Evo-X2 and others
			publisher.publish_tick({"world_time": new_time, "timestamp": int(time.time())})
			time.sleep(tick_interval)
	except Exception as e:
		import traceback
		print("[ChronicleKeeper] world_clock_loop encountered an error:")
		traceback.print_exc()

def start_world_clock():
	print("[ChronicleKeeper] start_world_clock called, launching thread...")
	t = threading.Thread(target=world_clock_loop, daemon=True)
	t.start()
