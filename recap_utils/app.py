import click
import click_pathlib
from pathlib import Path
import recap_argument_graph as ag
import recap_argument_graph_translator as agt
import typing as t
from dataclasses import field, dataclass


def rm_tree(pth: Path) -> None:
    """Remove the directory and all its contents.

    Args:
        pth: Path to be removed

    Returns:
        Nothing.

    Examples:
        >>> rm_tree(Path("data/out"))
    """
    for child in pth.iterdir():
        if child.is_file():
            child.unlink()
        else:
            rm_tree(child)
            child.rmdir()


@dataclass
class PathPair:
    """A pair of paths for modification of files."""

    source: Path
    target: Path


def pair_label(path_pair: t.Optional[PathPair]) -> str:
    """Generate a string for representing a path pair.

    Args:
        path_pair: The item that should be represented.

    Returns:
        A label for use in UI contexts.
    """

    if path_pair:
        return path_pair.source.name
    return ""


def path_pairs(
    folder_in: Path,
    folder_out: Path,
    suffix_in: str = ".json",
    suffix_out: str = ".json",
) -> t.List[PathPair]:
    files_in = list(folder_in.rglob(f"*{suffix_in}"))

    files_out = []
    for file_in in files_in:
        file_out = folder_out / file_in.relative_to(folder_in)
        file_out = file_out.with_suffix(suffix_out)
        file_out.parent.mkdir(parents=True, exist_ok=True)

        files_out.append(file_out)

    return [
        PathPair(file_in, file_out.with_suffix(suffix_out))
        for file_in, file_out in zip(files_in, files_out)
    ]


@click.group()
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
        rm_tree(folder_out)

    paths = path_pairs(folder_in, folder_out)
    translator = agt.Translator(auth_key, source_lang, target_lang)

    with click.progressbar(
        paths,
        label=f"Translating {folder_in}",
        item_show_func=pair_label,
        show_pos=True,
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
        rm_tree(folder_out)

    paths = path_pairs(folder_in, folder_out, suffix_out=".pdf")

    with click.progressbar(
        paths, label=f"Rendering {folder_in}", item_show_func=pair_label, show_pos=True,
    ) as bar:
        for path in bar:
            graph = ag.Graph.open(path.source)
            graph.render(path.target)


if __name__ == "__main__":
    cli()
