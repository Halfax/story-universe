"""Event handler registry and dispatcher.

This module provides a simple registry for event-specific handlers and a
dispatcher suitable for scheduling as a background task from the HTTP
ingest path. Handlers should accept (event_dict, db_conn_getter) and may
return a result or None.
"""

from typing import Any, Callable, Dict, Optional, List
import time

from services import event_consumer
from db.database import get_connection
from services import event_validator

# Mapping of event_type -> handler callable
_handlers: Dict[str, Callable[[Dict[str, Any], Optional[Callable[[], Any]]], Any]] = {}

# Middleware hooks
_pre_hooks: List[Callable[[Dict[str, Any], Optional[Callable[[], Any]]], None]] = []
_post_hooks: List[
    Callable[[Dict[str, Any], Optional[Callable[[], Any]], Optional[Any]], None]
] = []


def register_handler(
    event_type: str, func: Callable[[Dict[str, Any], Optional[Callable[[], Any]]], Any]
) -> None:
    if event_type not in _handlers:
        _handlers[event_type] = func


def register_pre_hook(
    func: Callable[[Dict[str, Any], Optional[Callable[[], Any]]], None],
) -> None:
    _pre_hooks.append(func)


def register_post_hook(
    func: Callable[[Dict[str, Any], Optional[Callable[[], Any]], Optional[Any]], None],
) -> None:
    _post_hooks.append(func)


def _ensure_processed_table():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """CREATE TABLE IF NOT EXISTS processed_events (event_id TEXT PRIMARY KEY, processed_ts INTEGER, status TEXT)"""
        )
        conn.commit()
        conn.close()
    except Exception:
        pass


def _has_processed(event_id: str) -> bool:
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT event_id FROM processed_events WHERE event_id = ?", (event_id,)
        )
        r = cur.fetchone()
        conn.close()
        return bool(r)
    except Exception:
        return False


def _mark_processed(event_id: str, status: str = "processed") -> None:
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT OR REPLACE INTO processed_events (event_id, processed_ts, status) VALUES (?, ?, ?)",
            (event_id, int(time.time()), status),
        )
        conn.commit()
        conn.close()
    except Exception:
        pass


def dispatch_event(
    event: Dict[str, Any], db_conn_getter: Optional[Callable[[], Any]] = None
) -> Optional[Any]:
    """Dispatch an event to a registered handler or the generic consumer.

    Adds middleware hooks (pre/post), idempotency checks via `processed_events`,
    and ensures schema-backed event types have handlers registered.
    """
    _ensure_processed_table()

    # Try to find canonical event id in metadata
    meta = event.get("metadata") or {}
    event_id = meta.get("_event_id") or event.get("id")
    if event_id and _has_processed(str(event_id)):
        # Already processed; skip
        return None

    etype = event.get("type")
    # Ensure schemas have handlers registered (map schema keys to generic consumer)
    try:
        for sk in getattr(event_validator, "EVENT_SCHEMAS", {}).keys():
            if sk not in _handlers:
                # map schema-named events to generic consumer (safe default)
                register_handler(
                    sk,
                    lambda ev, dbg=None: event_consumer.handle_event(
                        ev, db_conn_getter=dbg
                    ),
                )
    except Exception:
        pass

    handler = _handlers.get(etype)
    result = None
    try:
        # run pre hooks
        for h in _pre_hooks:
            try:
                h(event, db_conn_getter)
            except Exception:
                pass

        if handler:
            result = handler(event, db_conn_getter)
        else:
            result = event_consumer.handle_event(event, db_conn_getter=db_conn_getter)

        # run post hooks
        for h in _post_hooks:
            try:
                h(event, db_conn_getter, result)
            except Exception:
                pass

        # mark processed if we have an id
        if event_id:
            _mark_processed(str(event_id), status="processed")

        return result
    except Exception:
        import traceback

        traceback.print_exc()
        if event_id:
            _mark_processed(str(event_id), status="failed")
        return None


def dispatch_events_batch(
    events: List[Dict[str, Any]], db_conn_getter: Optional[Callable[[], Any]] = None
) -> None:
    """Dispatch multiple events efficiently. Groups tick/system events into a batch handler when possible."""
    # simple grouping: collect tick/system_tick events
    tick_events = [
        e for e in events if e.get("type") in ("system_tick", "world.tick", "tick")
    ]
    other_events = [e for e in events if e not in tick_events]

    # dispatch non-tick events individually
    for ev in other_events:
        dispatch_event(ev, db_conn_getter=db_conn_getter)

    if tick_events:
        # prefer a batch handler on the consumer if available
        if hasattr(event_consumer, "handle_tick_batch"):
            try:
                event_consumer.handle_tick_batch(
                    tick_events, db_conn_getter=db_conn_getter
                )
                for ev in tick_events:
                    meta = ev.get("metadata") or {}
                    eid = meta.get("_event_id") or ev.get("id")
                    if eid:
                        _mark_processed(str(eid), status="processed")
            except Exception:
                for ev in tick_events:
                    dispatch_event(ev, db_conn_getter=db_conn_getter)
        else:
            for ev in tick_events:
                dispatch_event(ev, db_conn_getter=db_conn_getter)


# Register common handlers by default
register_handler(
    "item_use", lambda ev, dbg=None: event_consumer.handle_event(ev, db_conn_getter=dbg)
)
register_handler(
    "item_use_decision",
    lambda ev, dbg=None: event_consumer.handle_event(ev, db_conn_getter=dbg),
)
