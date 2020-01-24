import click

from . import graph, text


@click.group()
def cli():
    pass


cli.add_command(graph.cli)
cli.add_command(text.cli)

if __name__ == "__main__":
    cli()
