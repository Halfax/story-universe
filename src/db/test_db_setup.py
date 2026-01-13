import sqlite3
import os


def setup_test_db(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute(
        """
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp INTEGER,
        type TEXT,
        description TEXT,
        involved_characters TEXT,
        involved_locations TEXT,
        metadata TEXT
    )
    """
    )
    c.execute(
        """
    CREATE TABLE IF NOT EXISTS system_state (
        key TEXT PRIMARY KEY,
        value TEXT
    )
    """
    )
    c.execute(
        """
    CREATE TABLE IF NOT EXISTS character_state (
        character_id INTEGER PRIMARY KEY,
        state TEXT,
        last_updated INTEGER
    )
    """
    )
    conn.commit()
    conn.close()


def teardown_test_db(db_path):
    if os.path.exists(db_path):
        # Try to gently close any lingering connections and retry removal
        try:
            # Opening and closing a connection can release some locks in certain Windows edge cases
            conn = sqlite3.connect(db_path)
            conn.close()
        except Exception:
            pass
        # Attempt removal with multiple retries in case of transient locks (Windows can be slow)
        import time
        import gc

        max_attempts = 30
        for attempt in range(1, max_attempts + 1):
            try:
                os.remove(db_path)
                return
            except PermissionError:
                # encourage GC and give OS a bit more time on later attempts
                try:
                    gc.collect()
                except Exception:
                    pass
                time.sleep(0.05 * attempt)

        # As a last-ditch effort, try truncating the file (may succeed if open handles allow)
        try:
            with open(db_path, "w"):
                pass
        except Exception:
            pass

        # Final attempt to remove; let exception propagate if still failing
        os.remove(db_path)
