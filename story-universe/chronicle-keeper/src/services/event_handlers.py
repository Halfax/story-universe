"""Event handler registry and dispatcher.

This module provides a simple registry for event-specific handlers and a
dispatcher suitable for scheduling as a background task from the HTTP
ingest path. Handlers should accept (event_dict, db_conn_getter) and may
return a result or None.
"""
from typing import Any, Callable, Dict, Optional

from src.services import event_consumer

# Mapping of event_type -> handler callable
_handlers: Dict[str, Callable[[Dict[str, Any], Optional[Callable[[], Any]]], Any]] = {}


def register_handler(event_type: str, func: Callable[[Dict[str, Any], Optional[Callable[[], Any]]], Any]) -> None:
    _handlers[event_type] = func


def dispatch_event(event: Dict[str, Any], db_conn_getter: Optional[Callable[[], Any]] = None) -> Optional[Any]:
    """Dispatch an event to a registered handler or the generic consumer.

    This function is intentionally synchronous so it can be scheduled with
    FastAPI's `BackgroundTasks.add_task`.
    """
    etype = event.get("type")
    handler = _handlers.get(etype)
    try:
        if handler:
            return handler(event, db_conn_getter)
        # Fallback: use the generic event consumer
        return event_consumer.handle_event(event, db_conn_getter=db_conn_getter)
    except Exception:
        import traceback

        traceback.print_exc()
        return None


# Register common handlers by default
register_handler("item_use", lambda ev, dbg=None: event_consumer.handle_event(ev, db_conn_getter=dbg))
register_handler("item_use_decision", lambda ev, dbg=None: event_consumer.handle_event(ev, db_conn_getter=dbg))
