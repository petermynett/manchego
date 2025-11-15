"""CLI commands for transaction import."""

import time

import typer

from manchego.cli.base import format_result
from manchego.transactions.loader import import_transactions
from manchego.utils.cli_audit import log_command_end, log_command_start
from manchego.utils.logging_helpers import generate_operation_id

transactions_app = typer.Typer(
    name="transactions",
    help="Transaction import and processing commands",
)


@transactions_app.command("import")
def import_cmd() -> None:
    """Import transaction files from raw directory into ledger."""
    # Generate operation_id
    operation_id = generate_operation_id("transactions_import")
    t0 = time.time()

    # Log command start
    log_command_start("transactions:import", {}, operation_id)

    typer.echo("🔄 Starting transaction import...")

    try:
        # Call business function
        result = import_transactions(operation_id=operation_id)

        # Log command end
        log_command_end("transactions:import", operation_id, result, time.time() - t0)

        # Format and display result
        format_result(result, "Transaction import")

    except Exception as e:
        # Log command end (failure)
        log_command_end(
            "transactions:import",
            operation_id,
            {"success": False, "error": str(e)},
            time.time() - t0,
        )

        # User-friendly error message
        typer.echo(f"❌ Transaction import failed: {e}", err=True)
        raise typer.Exit(1) from e
