# Tick Publisher

Overview
--------
The TickPublisher (and underlying `ZmqPub`) provides robust PUB socket
behavior for system ticks and events. It includes queueing, batching, and
reconnection logic to make the tick stream resilient to transient errors.

Recovery and Backoff
--------------------
- The publisher uses an exponential backoff strategy when reconnect attempts fail.
  - Base delay: `TICK_PUBLISHER_RECONNECT_DELAY` (default 0.5s)
  - Max delay: `TICK_PUBLISHER_MAX_RECONNECT_DELAY` (default 30s)
  - A small jitter (±20%) is applied to avoid thundering-herd reconnection attempts.
- Reconnect attempts are tracked and reset to 0 on a successful connection.

Queueing & Backpressure
-----------------------
- Messages are enqueued to a bounded queue (`TICK_PUBLISHER_MAX_QUEUE`).
- When the queue reaches a configured high-water threshold, a warning is logged
  and `high_water_events` metric is incremented.
- If the queue is full, messages are dropped and optionally written to a dead-letter
  file (`TICK_PUBLISHER_DEAD_LETTER_FILE`).

Batching
--------
- Tick messages are batched up to `TICK_PUBLISHER_BATCH_SIZE` when the sender
  thread drains the queue. Batches are published as a single `tick_batch` message
  to reduce publish overhead.

Configuration
-------------
Relevant configuration values (in `shared/config.py`):

- `TICK_PUBLISHER_RECONNECT_DELAY` — base reconnect delay (seconds).
- `TICK_PUBLISHER_MAX_RECONNECT_DELAY` — maximum reconnect backoff (seconds).
- `TICK_PUBLISHER_MAX_QUEUE` — maximum in-memory send queue size.
- `TICK_PUBLISHER_DEAD_LETTER_FILE` — path to append dropped messages.
- `TICK_PUBLISHER_BACKPRESSURE_THRESHOLD` — high-water threshold (absolute number or fraction, code treats as int threshold).
- `TICK_PUBLISHER_BATCH_SIZE` — number of ticks to batch in one message.
- `TICK_PUBLISHER_LAG_WARN_THRESHOLD` — latency (seconds) that triggers warnings.

Testing
-------
Unit tests include `tests/test_publisher_queue.py` for queue behavior and
`tests/test_tick_publisher_recovery.py` for basic reconnection/retry behavior.

Operational notes
-----------------
- For production, ensure the dead-letter file path is writable by the service user.
- Tune `TICK_PUBLISHER_MAX_QUEUE` and `TICK_PUBLISHER_BACKPRESSURE_THRESHOLD` to
  match expected publish rates and available memory.
