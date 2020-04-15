import logging
import typing as t

import deepl_pro as dl
import recap_argument_graph as ag

log = logging.getLogger(__name__)


class Translator:
    trans_plain: dl.Translator
    trans_xml: dl.Translator

    def __init__(self, auth_key: str, source_lang: str, target_lang: str):
        self.trans_plain = dl.Translator(
            auth_key,
            source_lang,
            target_lang,
            preserve_formatting=dl.Formatting.PRESERVE,
        )

        self.trans_xml = dl.Translator(
            auth_key,
            source_lang,
            target_lang,
            preserve_formatting=dl.Formatting.PRESERVE,
            tag_handling=dl.TagHandling.XML,
            outline_detection=dl.Outline.IGNORE,
        )

    def translate_graph(self, graph: ag.Graph, parallel: bool = False) -> None:
        graph.text = self.trans_plain.translate_text(graph.text)

        if graph.highlighted_text:
            graph.highlighted_text = self.trans_xml.translate_text(
                graph.highlighted_text.replace("<br>", "\n")
            ).replace("\n", "<br>")

        texts = [inode.text for inode in graph.inodes]
        translations = self.trans_plain.translate_texts(texts, parallel=parallel)

        for inode, translation in zip(graph.inodes, translations):
            inode.text = translation

    def translate_graphs(
        self, graphs: t.Iterable[ag.Graph], parallel: bool = False
    ) -> None:
        for graph in graphs:
            self.translate_graph(graph, parallel)
