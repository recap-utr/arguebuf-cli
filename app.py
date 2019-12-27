import click
from pathlib import Path
import recap_argument_graph as ag
import recap_argument_graph_translator as agt
import recap_deepl_pro as dl

log = logging.getLogger(__name__)


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
@click.argument("folder_in")
@click.argument("folder_out")
@click.option("--source-lang")
@click.option("--target-lang")
@click.option("--auth-key")
def translate(
    folder_in: str, folder_out: str, source_lang: str, target_lang: str, auth_key: str
):
    folder_in = Path(folder_in)
    # TODO: file_out = path_out / file_in.relative_to(path_in)
    folder_out = Path(folder_out)
    source_lang = dl.Language(source_lang)
    target_lang = dl.Language(target_lang)

    folder_out.mkdir(parents=True, exist_ok=True)
    rm_tree(folder_out)

    graphs = ag.Graph.open_folder(folder_in)
    translator = agt.Translator(auth_key, source_lang, target_lang)

    log.info(f"Total files: {len(graphs)}")

    for i, graph in enumerate(graphs):
        log.info(f"Translating {i}/{len(graphs)}.")

        translator.translate_graph(graph)
        graph.save(folder_out)
        graph.render(folder_out)


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
