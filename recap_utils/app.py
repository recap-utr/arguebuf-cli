import click
import click_pathlib
from pathlib import Path
import recap_argument_graph as ag
import recap_argument_graph_translator as agt
import typing as t
from dataclasses import field, dataclass


def rm_tree(pth: Path) -> None:
    for child in pth.iterdir():
        if child.is_file():
            child.unlink()
        else:
            rm_tree(child)
            child.rmdir()


@dataclass
class PathPair:
    source: Path
    target: Path


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
    "folder_in", type=click_pathlib.Path(exists=True),
)
@click.argument(
    "folder_out", type=click_pathlib.Path(exists=True),
)
@click.option("--source-lang", required=True)
@click.option("--target-lang", required=True)
@click.option("--auth-key", required=True)
@click.option("--clean/--no-clean", default=True)
@click.option("--parallel/--sequential", default=True)
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

    total_files = len(paths)
    print(f"Total files: {total_files}")

    for i, path in enumerate(paths):
        print(f"Translating '{path.source}' ({i}/{total_files}).")

        graph = ag.Graph.open(path.source)
        translator.translate_graph(graph, parallel)
        graph.save(path.target)


@cli.command()
@click.argument(
    "folder_in", type=click_pathlib.Path(exists=True),
)
@click.argument(
    "folder_out", type=click_pathlib.Path(exists=True),
)
@click.option("--clean/--no-clean", default=True)
def render(folder_in: Path, folder_out: Path, clean: bool) -> None:
    if clean:
        rm_tree(folder_out)

    paths = path_pairs(folder_in, folder_out, suffix_out=".pdf")

    total_files = len(paths)
    print(f"Total files: {total_files}")

    for i, path in enumerate(paths):
        print(f"Rendering '{path.source}' ({i}/{total_files}).")

        graph = ag.Graph.open(path.source)
        graph.render(path.target)


if __name__ == "__main__":
    cli()
