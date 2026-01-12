


try:
	print("[ChronicleKeeper] clock.py starting up...", flush=True)
	from src.db.database import get_connection
	from src.messaging.publisher import TickPublisher
except Exception as import_exc:
	import traceback
	print("[ChronicleKeeper] Import error in clock.py:", flush=True)
	traceback.print_exc()
	raise

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
	print("[ChronicleKeeper] world_clock_loop thread starting...", flush=True)
	try:
		publisher = TickPublisher()
		print("[ChronicleKeeper] TickPublisher created.", flush=True)
		while True:
			try:
				conn = get_connection()
				print("[ChronicleKeeper] Got DB connection.", flush=True)
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
				print(f"[PI] World time advanced to {new_time}", flush=True)
				# Broadcast tick to Evo-X2 and others
				publisher.publish_tick({"world_time": new_time, "timestamp": int(time.time())})
			except Exception as loop_exc:
				import traceback
				print("[ChronicleKeeper] Error in world_clock_loop tick:", flush=True)
				traceback.print_exc()
			time.sleep(tick_interval)
	except Exception as e:
		import traceback
		print("[ChronicleKeeper] world_clock_loop encountered an error:", flush=True)
		traceback.print_exc()


def start_world_clock():
	print("[ChronicleKeeper] start_world_clock called, launching thread...", flush=True)
	t = threading.Thread(target=world_clock_loop, daemon=True)
	t.start()

# Top-level error catch for script run
if __name__ == "__main__":
	try:
		print("[ChronicleKeeper] clock.py __main__ entry", flush=True)
		start_world_clock()
		while True:
			time.sleep(60)
	except Exception as main_exc:
		import traceback
		print("[ChronicleKeeper] Fatal error in clock.py __main__:", flush=True)
		traceback.print_exc()
