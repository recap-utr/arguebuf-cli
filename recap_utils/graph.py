import shutil
from pathlib import Path

import click
import click_pathlib
import recap_argument_graph as ag

from . import model, graph_translator


@click.group("graph")
def cli() -> None:
    pass


@cli.command()
@click.argument(
    "folder_in", type=click_pathlib.Path(exists=True, file_okay=False),
)
@click.argument(
    "folder_out", type=click_pathlib.Path(exists=True, file_okay=False),
)
@click.option(
    "--source-lang", required=True, help="Lowercase code, i.e. en for English."
)
@click.option(
    "--target-lang", required=True, help="Lowercase code, i.e. en for English."
)
@click.option("--auth-key", required=True, help="DeepL Pro API key.")
@click.option(
    "--clean/--no-clean", default=False, help="Remove all contents of FOLDER_OUT."
)
@click.option(
    "--parallel/--sequential",
    default=True,
    help="Send multiple requests to DeepL at the same time.",
)
@click.option("--start", default=1, help="Start index.")
def translate(
    folder_in: Path,
    folder_out: Path,
    source_lang: str,
    target_lang: str,
    auth_key: str,
    clean: bool,
    parallel: bool,
    start: int,
) -> None:
    if clean:
        shutil.rmtree(folder_out)
        folder_out.mkdir()

    paths = model.PathPair.create(folder_in, folder_out, ".json", ".json")
    translator = graph_translator.Translator(auth_key, source_lang, target_lang)

    with click.progressbar(
        paths[start - 1 :], item_show_func=model.PathPair.label, show_pos=True,
    ) as bar:
        for path in bar:
            graph = ag.Graph.open(path.source)
            translator.translate_graph(graph, parallel)
            graph.save(path.target)


@cli.command()
@click.argument(
    "folder_in", type=click_pathlib.Path(exists=True, file_okay=False),
)
@click.argument(
    "folder_out", type=click_pathlib.Path(exists=True, file_okay=False),
)
@click.option(
    "--node-label",
    default="plain_text",
    help="Node attribute that should be used as a label.",
)
@click.option(
    "--clean/--no-clean", default=False, help="Remove all contents of FOLDER_OUT."
)
@click.option("--start", default=1, help="Start index.")
def render(
    folder_in: Path, folder_out: Path, node_label: str, clean: bool, start: int
) -> None:
    if clean:
        shutil.rmtree(folder_out)
        folder_out.mkdir()

    paths = model.PathPair.create(folder_in, folder_out, ".json", ".pdf")

    with click.progressbar(
        paths[start - 1 :], item_show_func=model.PathPair.label, show_pos=True,
    ) as bar:
        for path_pair in bar:
            if not path_pair.target.exists():
                graph = ag.Graph.open(path_pair.source)
                graph.render(path_pair.target, node_label=node_label)


@cli.command()
@click.argument(
    "folder_in", type=click_pathlib.Path(exists=True, file_okay=False),
)
@click.argument(
    "folder_out", type=click_pathlib.Path(exists=True, file_okay=False),
)
@click.option(
    "--input-format",
    required=True,
    type=click.Choice([".json", ".ann"]),
    help="Input format of the files.",
)
@click.option(
    "--output-format",
    required=True,
    type=click.Choice(["aif", "ova"]),
    help="Output format of the json files.",
)
@click.option(
    "--clean/--no-clean", default=False, help="Remove all contents of FOLDER_OUT."
)
@click.option("--start", default=1, help="Start index.")
def convert(
    folder_in: Path,
    folder_out: Path,
    input_format: str,
    output_format: str,
    clean: bool,
    start: int,
) -> None:
    if clean:
        shutil.rmtree(folder_out)
        folder_out.mkdir()

    paths = model.PathPair.create(folder_in, folder_out, input_format, ".json")

    with click.progressbar(
        paths[start - 1 :], item_show_func=model.PathPair.label, show_pos=True,
    ) as bar:
        for path_pair in bar:
            if not path_pair.target.exists():
                graph = ag.Graph.open(path_pair.source)
                graph.category = ag.GraphCategory(output_format)
                graph.save(path_pair.target)


@cli.command()
@click.argument(
    "folder_in", type=click_pathlib.Path(exists=True, file_okay=False),
)
@click.option(
    "--input-format",
    required=True,
    type=click.Choice([".json", ".ann"]),
    help="Input format of the files.",
)
def count(folder_in: Path, input_format: str):
    files = sorted(folder_in.rglob(f"*{input_format}"))
    graphs = [ag.Graph.open(file) for file in files]
    inodes = [len(graph.inodes) for graph in graphs]
    snodes = [len(graph.snodes) for graph in graphs]
    edges = [len(graph.edges) for graph in graphs]

    total_graphs = len(graphs)
    total_inodes = sum(inodes)
    total_snodes = sum(snodes)
    total_edges = sum(edges)

    click.echo(
        f"""Total Graphs: {total_graphs}

Total I-nodes: {total_inodes}
Total S-nodes: {total_snodes}
Total Edges: {total_edges}

I-nodes per Graph: {total_inodes / total_graphs}
S-nodes per Graph: {total_snodes / total_graphs}
Edges per Graph: {total_edges / total_graphs}

Max. I-nodes: {max(inodes)}
Max. S-nodes: {max(snodes)}
Max. Edges: {max(edges)}

Min. I-nodes: {min(inodes)}
Min. S-nodes: {min(snodes)}
Min. Edges: {min(edges)}"""
    )
