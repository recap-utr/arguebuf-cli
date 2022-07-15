import typer

from arguebuf_cli import graph, text

cli = typer.Typer()
cli.add_typer(
    graph.cli, name="graph", help="Command group for dealing with argument graphs."
)
cli.add_typer(text.cli, name="text", help="Command group for dealing with plain texts.")

if __name__ == "__main__":
    cli()
