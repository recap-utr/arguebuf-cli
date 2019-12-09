import click
from pathlib import Path
import argument_graph as ag


def rm_tree(pth: Path):
    for child in pth.iterdir():
        if child.is_file():
            child.unlink()
        else:
            rm_tree(child)
            child.rmdir()


@click.group()
def cli():
    pass


@cli.command()
def translate():
    pass


@cli.command()
@click.argument("folder_in")
@click.argument("folder_out")
def draw(folder_in, folder_out):
    folder_in = Path(folder_in)
    folder_out = Path(folder_out)

    folder_out.mkdir(parents=True, exist_ok=True)
    rm_tree(folder_out)

    graphs = ag.Graph.from_folder(folder_in)

    for graph in graphs:
        graph.draw(folder_out)


cli()
