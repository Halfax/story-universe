"""
Middleware package for Chronicle Keeper.

This package contains middleware components that can be used to process requests
and responses in the FastAPI application.
"""

# Import middleware classes to make them available when importing from the package
from .event_validation import EventValidationMiddleware

# Define what gets imported with 'from middleware import *'
__all__ = ["EventValidationMiddleware"]
