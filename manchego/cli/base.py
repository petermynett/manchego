"""Base CLI utilities for formatting results."""

import typer


def format_result(result: dict, operation_name: str) -> None:
    """Format and display operation result to console.

    Args:
        result: Result dict with success, total, succeeded, failed, etc.
        operation_name: Human-readable operation name.
    """
    if result.get("success"):
        typer.echo(f"✅ {operation_name} completed successfully")
    else:
        typer.echo(f"⚠️ {operation_name} completed with errors")

    if "total" in result:
        typer.echo(f"   Total files: {result['total']}")
    if "succeeded" in result:
        typer.echo(f"   ✅ Succeeded: {result['succeeded']}")
    if "failed" in result and result["failed"] > 0:
        typer.echo(f"   ❌ Failed: {result['failed']}")

    if "elapsed_s" in result:
        typer.echo(f"   ⏱️ Time: {result['elapsed_s']:.2f}s")

    if result.get("failures"):
        typer.echo("\n   Failures:")
        for failure in result["failures"]:
            file = failure.get("file", "unknown")
            reason = failure.get("reason", "unknown error")
            typer.echo(f"   - {file}: {reason}")
