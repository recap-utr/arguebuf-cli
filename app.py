import click
from pathlib import Path
import recap_argument_graph as ag
import recap_argument_graph_translator as agt
import recap_deepl_pro as dl
import typing as t

log = logging.getLogger(__name__)


def rm_tree(pth: Path):
    for child in pth.iterdir():
        if child.is_file():
            child.unlink()
        else:
            rm_tree(child)
            child.rmdir()


def list_folder(path: Path) -> t.List[Path]:
    return list(path.rglob("*.json"))


def reconstruct_hierarchy(
    files_in: t.Iterable[Path], folder_in: Path, folder_out: Path
) -> t.List[Path]:
    return [folder_out / file_in.relative_to(folder_in) for file_in in files_in]


@click.group()
def cli():
    pass


@cli.command()
@click.argument("folder_in")
@click.argument("folder_out")
@click.option("--source-lang")
@click.option("--target-lang")
@click.option("--auth-key")
def translate(
    folder_in: str, folder_out: str, source_lang: str, target_lang: str, auth_key: str
):
    folder_in = Path(folder_in)
    folder_out = Path(folder_out)
    source_lang = dl.Language(source_lang)
    target_lang = dl.Language(target_lang)

    files_in = list_folder(folder_in)
    files_out = reconstruct_hierarchy(files_in, folder_in, folder_out)
    total_files = len(files_in)

    folder_out.mkdir(parents=True, exist_ok=True)
    rm_tree(folder_out)

    translator = agt.Translator(auth_key, source_lang, target_lang)

    log.info(f"Total files: {total_files}")

    for i, (file_in, file_out) in enumerate(zip(files_in, files_out)):
        log.info(f"Translating {i}/{total_files}.")

        graph = ag.Graph.open(file_in)
        translator.translate_graph(graph)
        graph.save(file_out)


@cli.command()
@click.argument("folder_in")
@click.argument("folder_out")
def render(folder_in: str, folder_out: str):
    folder_in = Path(folder_in)
    folder_out = Path(folder_out)

    folder_out.mkdir(parents=True, exist_ok=True)
    rm_tree(folder_out)

    graphs = ag.Graph.open_folder(folder_in)

    for graph in graphs:
        graph.render(folder_out)


if __name__ == "__main__":
    cli()
