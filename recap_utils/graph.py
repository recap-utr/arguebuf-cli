import shutil
import typing as t
from enum import Enum
from pathlib import Path

import arguebuf as ag
import typer

from recap_utils import graph_translator, model

cli = typer.Typer()


@cli.command()
def translate(
    folder_in: Path,
    folder_out: Path,
    source_lang: str,
    target_lang: str,
    auth_key: str,
    input_glob: str,
    output_format: ag.GraphFormat = ag.GraphFormat.ARGUEBUF,
    clean: bool = False,
    overwrite: bool = False,
    parallel: bool = True,
    start: int = 1,
) -> None:
    if clean:
        shutil.rmtree(folder_out)
        folder_out.mkdir()

    path_pairs = model.PathPair.create(folder_in, folder_out, input_glob, ".json")
    translator = graph_translator.Translator(auth_key, source_lang, target_lang)

    with typer.progressbar(
        path_pairs[start - 1 :],
        item_show_func=model.PathPair.label,
        show_pos=True,
    ) as bar:
        for path_pair in bar:
            if overwrite or not path_pair.target.exists():
                graph = ag.Graph.from_file(path_pair.source)
                translator.translate_graph(graph, parallel)
                graph.to_file(path_pair.target, output_format)


@cli.command()
def render(
    folder_in: Path,
    folder_out: Path,
    input_glob: str,
    output_format: str = ".pdf",
    nodesep: t.Optional[float] = None,
    ranksep: t.Optional[float] = None,
    node_wrap_col: t.Optional[int] = None,
    node_margin: t.Optional[t.Tuple[float, float]] = None,
    font_name: t.Optional[str] = None,
    font_size: t.Optional[float] = None,
    clean: bool = False,
    overwrite: bool = False,
    start: int = 1,
) -> None:
    if clean:
        shutil.rmtree(folder_out)
        folder_out.mkdir()

    paths = model.PathPair.create(folder_in, folder_out, input_glob, output_format)

    with typer.progressbar(
        paths[start - 1 :],
        item_show_func=model.PathPair.label,
        show_pos=True,
    ) as bar:
        for path_pair in bar:
            if overwrite or not path_pair.target.exists():
                graph = ag.Graph.from_file(path_pair.source).to_gv(
                    format=output_format.replace(".", ""),
                    nodesep=nodesep,
                    ranksep=ranksep,
                    wrap_col=node_wrap_col,
                    margin=node_margin,
                    font_name=font_name,
                    font_size=font_size,
                )
                ag.render(graph, path_pair.target)


@cli.command()
def convert(
    folder_in: Path,
    folder_out: Path,
    input_glob: str,
    output_format: ag.GraphFormat = ag.GraphFormat.ARGUEBUF,
    clean: bool = False,
    overwrite: bool = False,
    start: int = 1,
) -> None:
    if clean:
        shutil.rmtree(folder_out)
        folder_out.mkdir()

    paths = model.PathPair.create(folder_in, folder_out, input_glob, ".json")

    with typer.progressbar(
        paths[start - 1 :],
        item_show_func=model.PathPair.label,
        show_pos=True,
    ) as bar:
        for path_pair in bar:
            if overwrite or not path_pair.target.exists():
                graph = ag.Graph.from_file(path_pair.source)
                graph.to_file(path_pair.target, output_format)


@cli.command()
def statistics(
    folder_in: Path,
    input_glob: str,
):
    files = sorted(folder_in.glob(input_glob))

    graphs = [ag.Graph.from_file(file) for file in files]
    atom_nodes = [len(graph.atom_nodes) for graph in graphs]
    scheme_nodes = [len(graph.scheme_nodes) for graph in graphs]
    edges = [len(graph.edges) for graph in graphs]

    total_graphs = len(graphs)
    total_atom_nodes = sum(atom_nodes)
    total_scheme_nodes = sum(scheme_nodes)
    total_edges = sum(edges)

    typer.echo(
        f"""Total Graphs: {total_graphs}

Total Atom Nodes: {total_atom_nodes}
Total Scheme Nodes: {total_scheme_nodes}
Total Edges: {total_edges}

Atom Nodes per Graph: {total_atom_nodes / total_graphs}
Scheme Nodes per Graph: {total_scheme_nodes / total_graphs}
Edges per Graph: {total_edges / total_graphs}

Max. Atom Nodes: {max(atom_nodes)}
Max. Scheme Nodes: {max(scheme_nodes)}
Max. Edges: {max(edges)}

Min. Atom Nodes: {min(atom_nodes)}
Min. Scheme Nodes: {min(scheme_nodes)}
Min. Edges: {min(edges)}"""
    )
