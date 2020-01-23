import click

from . import graph, txt


@click.group()
def cli():
    pass


cli.add_command(graph.cli)
cli.add_command(txt.cli)

if __name__ == "__main__":
    cli()
