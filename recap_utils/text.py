import shutil
from pathlib import Path

import click
import click_pathlib
import deepl_pro as dl

from recap_utils import model


@click.group("text")
def cli() -> None:
    pass


@cli.command()
@click.argument(
    "folder_in",
    type=click_pathlib.Path(),
)
@click.argument(
    "folder_out",
    type=click_pathlib.Path(),
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
@click.option("--suffix", default=".txt")
@click.option("--start", default=1, help="Start index.")
def translate(
    folder_in: Path,
    folder_out: Path,
    source_lang: str,
    target_lang: str,
    auth_key: str,
    clean: bool,
    suffix: str,
    start: int,
) -> None:
    if clean:
        shutil.rmtree(folder_out)
        folder_out.mkdir()

    paths = model.PathPair.create(folder_in, folder_out, suffix, suffix)
    translator = dl.Translator(
        auth_key, dl.Language(source_lang), dl.Language(target_lang)
    )

    with click.progressbar(
        paths[start - 1 :],
        item_show_func=model.PathPair.label,
        show_pos=True,
    ) as bar:
        for path_pair in bar:
            if not path_pair.target.exists():
                with path_pair.source.open("r") as file:
                    source_text = file.read()

                target_text = translator.translate_text(source_text)

                with path_pair.target.open("w") as file:
                    file.write(target_text)
