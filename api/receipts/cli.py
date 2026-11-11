import typer

from receipts.settings import ConfigError, check_settings, get_settings

app = typer.Typer(help="Ledgit command line", no_args_is_help=True)


@app.command()
def check() -> None:
    """Validate environment configuration."""
    try:
        check_settings(get_settings())
    except ConfigError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(1) from exc
    typer.echo("configuration ok")


if __name__ == "__main__":
    app()
