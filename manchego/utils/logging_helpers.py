"""Logging helper functions for operation ID generation and structured logging."""

from datetime import UTC, datetime
from uuid import uuid4


def generate_operation_id(operation_name: str) -> str:
    """Generate a unique operation ID for tracing.

    Format: {operation_name}_{YYYYMMDD}_{HHMMSS}_{short_uuid}

    Args:
        operation_name: Operation identifier in snake_case.

    Returns:
        str: Unique operation ID.
    """
    now = datetime.now(UTC)
    date_str = now.strftime("%Y%m%d")
    time_str = now.strftime("%H%M%S")
    short_uuid = str(uuid4())[:8]

    return f"{operation_name}_{date_str}_{time_str}_{short_uuid}"
