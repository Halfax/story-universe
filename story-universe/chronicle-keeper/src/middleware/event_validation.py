"""
Event Validation Middleware
--------------------------
This module provides middleware for validating events before they are processed by the API.
It integrates with the existing CanonicalEvent model and adds additional validation rules.
"""

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Callable, Awaitable, Dict, Any, Optional
import json
import logging
from datetime import datetime
from uuid import UUID, uuid4
import re

from src.models.canonical_event import CanonicalEvent
from src.services.event_validator import EventValidator

logger = logging.getLogger(__name__)


class EventValidationMiddleware:
    """Middleware for validating events before they reach the API endpoints."""

    def __init__(self, app, validator: Optional[EventValidator] = None):
        """Initialize the middleware.

        Args:
            app: The FastAPI application
            validator: Optional EventValidator instance (will create one if not provided)
        """
        self.app = app
        self.validator = validator or EventValidator(strict=True)

    async def __call__(
        self, request: Request, call_next: Callable[[Request], Awaitable]
    ) -> Any:
        """Process the request and validate events."""
        # Only process /event endpoint
        if request.url.path != "/event" or request.method != "POST":
            return await call_next(request)

        try:
            # Parse request body
            body = await request.body()
            event = json.loads(body)

            # Generate ID if not present (to match existing behavior)
            if "id" not in event or not event.get("id"):
                event["id"] = (
                    f"evt_{int(datetime.utcnow().timestamp())}_{uuid4().hex[:8]}"
                )

            # Validate against CanonicalEvent model first
            try:
                parsed = (
                    CanonicalEvent.model_validate(event)
                    if hasattr(CanonicalEvent, "model_validate")
                    else CanonicalEvent(**event)
                )
                event_data = (
                    parsed.dict() if hasattr(parsed, "dict") else parsed.model_dump()
                )
            except Exception as e:
                logger.warning(f"Event validation failed (schema): {str(e)}")
                return JSONResponse(
                    status_code=status.HTTP_200_OK,  # Maintain backward compatibility
                    content={
                        "status": "rejected",
                        "reason": f"schema validation failed: {str(e)}",
                    },
                )

            # Run custom validations
            is_valid, errors = self.validator.validate(event_data)
            if not is_valid:
                logger.warning(f"Event validation failed (custom): {errors}")
                return JSONResponse(
                    status_code=status.HTTP_200_OK,  # Maintain backward compatibility
                    content={
                        "status": "rejected",
                        "reason": f"validation failed: {', '.join(errors)}",
                    },
                )

            # If validation passes, update the request with the validated event
            request.state.validated_event = event_data

            # Continue processing the request
            return await call_next(request)

        except json.JSONDecodeError:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"status": "error", "reason": "Invalid JSON payload"},
            )
        except Exception as e:
            logger.exception("Unexpected error during event validation")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "status": "error",
                    "reason": "Internal server error during validation",
                },
            )
