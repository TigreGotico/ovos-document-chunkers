from typing import Iterable

from quebra_frases import paragraph_tokenize

from ovos_document_chunkers.base import AbstractTextDocumentChunker
from ovos_document_chunkers.text.sentence import WtPSentenceSplitter, SaTSentenceSplitter


class RegexParagraphSplitter(AbstractTextDocumentChunker):
    def chunk(self, data: str) -> Iterable[str]:
        for c in data.split("\n"):
            for p in paragraph_tokenize(c):
                yield p


class WtPParagraphSplitter(WtPSentenceSplitter):

    def chunk(self, data: str) -> Iterable[str]:
        yield from self.splitter.split(data, do_paragraph_segmentation=True)


class SaTParagraphSplitter(SaTSentenceSplitter):

    def chunk(self, data: str) -> Iterable[str]:
        yield from self.splitter.split(data, do_paragraph_segmentation=True)
