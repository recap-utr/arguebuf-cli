import shutil
from pathlib import Path

import click
import click_pathlib
import recap_argument_graph as ag
import recap_argument_graph_translator as agt

from . import model


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
def translate(
    folder_in: Path,
    folder_out: Path,
    source_lang: str,
    target_lang: str,
    auth_key: str,
    clean: bool,
    parallel: bool,
) -> None:
    if clean:
        shutil.rmtree(folder_out)
        folder_out.mkdir()

    paths = model.PathPair.create(folder_in, folder_out, ".json", ".json")
    translator = agt.Translator(auth_key, source_lang, target_lang)

    with click.progressbar(
        paths, label="Translating…", item_show_func=model.PathPair.label, show_pos=True,
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
    "--clean/--no-clean", default=False, help="Remove all contents of FOLDER_OUT."
)
def render(folder_in: Path, folder_out: Path, clean: bool) -> None:
    if clean:
        shutil.rmtree(folder_out)
        folder_out.mkdir()

    paths = model.PathPair.create(folder_in, folder_out, ".json", ".pdf")

    with click.progressbar(
        paths, label="Rendering…", item_show_func=model.PathPair.label, show_pos=True,
    ) as bar:
        for path_pair in bar:
            if not path_pair.target.exists():
                graph = ag.Graph.open(path_pair.source)
                graph.render(path_pair.target)
