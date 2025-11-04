"""CLI entry point for manchego."""

import typer

app = typer.Typer(
    help="Data management system to help track my time and money",
    add_completion=False,
    no_args_is_help=True,
)


@app.callback(invoke_without_command=True)
def main_callback(ctx: typer.Context) -> None:
    """Main callback for manchego CLI."""
    if ctx.invoked_subcommand is None:
        typer.echo("Use 'manchego --help' to see available commands.")


@app.command()
def version() -> None:
    """Show manchego version."""
    typer.echo("manchego 0.1.0")


def main() -> None:
    """Entry point for manchego CLI."""
    app()


if __name__ == "__main__":
    main()

