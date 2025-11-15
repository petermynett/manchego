"""CLI audit logging for command invocations."""

import json
import logging
import os
from datetime import UTC, datetime
from pathlib import Path

import manchego.global_config as g

logger = logging.getLogger(__name__)

# CLI audit log path
CLI_AUDIT_LOG = g.LOGS_ROOT / "cli" / "commands.log"


def log_command_start(command: str, args: dict, operation_id: str) -> None:
    """Log CLI command start to audit trail.

    Args:
        command: Command name (e.g., "transactions:import").
        args: Command arguments as dict.
        operation_id: Operation ID for tracing.
    """
    CLI_AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)

    entry = {
        "timestamp": datetime.now(UTC).isoformat(),
        "level": "INFO",
        "event": "command_start",
        "command": command,
        "operation_id": operation_id,
        "args": args,
        "user": os.getenv("USER", "unknown"),
        "cwd": str(Path.cwd()),
    }

    with open(CLI_AUDIT_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def log_command_end(
    command: str, operation_id: str, result: dict, elapsed_s: float
) -> None:
    """Log CLI command end to audit trail.

    Args:
        command: Command name (e.g., "transactions:import").
        operation_id: Operation ID for tracing.
        result: Command result dict.
        elapsed_s: Elapsed time in seconds.
    """
    CLI_AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)

    entry = {
        "timestamp": datetime.now(UTC).isoformat(),
        "level": "INFO",
        "event": "command_end",
        "command": command,
        "operation_id": operation_id,
        "result": result,
        "elapsed_s": elapsed_s,
    }

    with open(CLI_AUDIT_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
