import shutil
from pathlib import Path

import deepl_pro as dl
import typer

from recap_utils import model

cli = typer.Typer()


@cli.command()
def translate(
    folder_in: Path,
    folder_out: Path,
    source_lang: str,
    target_lang: str,
    auth_key: str,
    input_glob: str,
    output_suffix: str,
    clean: bool = False,
    overwrite: bool = False,
    start: int = 1,
) -> None:
    if clean:
        shutil.rmtree(folder_out)
        folder_out.mkdir()

    paths = model.PathPair.create(folder_in, folder_out, input_glob, output_suffix)
    translator = dl.Translator(
        auth_key, dl.Language(source_lang), dl.Language(target_lang)
    )

    with typer.progressbar(
        paths[start - 1 :],
        item_show_func=model.PathPair.label,
        show_pos=True,
    ) as bar:
        for path_pair in bar:
            if overwrite or not path_pair.target.exists():
                with path_pair.source.open("r") as file:
                    source_text = file.read()

                target_text = translator.translate_text(source_text)

                with path_pair.target.open("w") as file:
                    file.write(target_text)
