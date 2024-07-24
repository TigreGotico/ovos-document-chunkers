from typing import Iterable, Dict

from quebra_frases import sentence_tokenize, paragraph_tokenize

from ovos_document_chunkers.base import AbstractTextDocumentChunker


class RegexSentenceSplitter(AbstractTextDocumentChunker):
    def __init__(self, config: Dict = None):
        config = config or {}
        super().__init__(config)

    def chunk(self, data: str) -> Iterable[str]:
        for c in data.split("\n"):
            for p in paragraph_tokenize(c):
                for s in sentence_tokenize(p):
                    yield s


class PySBDSentenceSplitter(AbstractTextDocumentChunker):
    def __init__(self, config: Dict = None):
        config = config or {"lang": "en"}
        super().__init__(config)
        import pysbd
        self.splitter = pysbd.Segmenter(language=self.config.get("lang", "en"),
                                        clean=False)

    def chunk(self, data: str) -> Iterable[str]:
        return self.splitter.segment(data)


class SaTSentenceSplitter(AbstractTextDocumentChunker):
    VALID_MODELS = [
        "sat-1l",
        "sat-3l",
        "sat-3l-sm",
        "sat-3l-lora",
        "sat-6l",
        "sat-6l-sm",
        "sat-9l",
        "sat-9l-sm",
        "sat-12l",
        "sat-12l-sm",
        "sat-12l-lora"
    ]

    def __init__(self, config: Dict = None):
        config = config or {"model": "sat-3l-sm"}
        super().__init__(config)
        from wtpsplit import SaT
        self.model = self.config["model"]
        assert self.model in self.VALID_MODELS

        cuda = self.config.get("use_cuda")
        self.splitter = SaT(self.model)
        if cuda:
            self.splitter.half().to("cuda")

    def chunk(self, data: str) -> Iterable[str]:
        yield from self.splitter.split(data, do_paragraph_segmentation=False)


class WtPSentenceSplitter(AbstractTextDocumentChunker):
    VALID_MODELS = [
        "wtp-bert-tiny",
        "wtp-bert-mini",
        "wtp-canine-s-1l",
        "wtp-canine-s-1l-no-adapters",
        "wtp-canine-s-3l",
        "wtp-canine-s-3l-no-adapters",
        "wtp-canine-s-6l",
        "wtp-canine-s-6l-no-adapters",
        "wtp-canine-s-9l",
        "wtp-canine-s-9l-no-adapters",
        "wtp-canine-s-12l",
        "wtp-canine-s-12l-no-adapters"
    ]

    def __init__(self, config: Dict = None):
        config = config or {"model": "wtp-bert-mini"}
        super().__init__(config)
        from wtpsplit import WtP
        self.model = self.config["model"]
        assert self.model in self.VALID_MODELS

        cuda = self.config.get("use_cuda")
        if "bert" in self.model and self.config.get("use_onnx", True):  # use onnxruntime
            self.splitter = WtP(self.model,
                                ort_providers=['CUDAExecutionProvider' if cuda
                                               else 'CPUExecutionProvider'])
        else:  # pytorch needed
            self.splitter = WtP(self.model)
            if cuda:
                self.splitter.half().to("cuda")

    def chunk(self, data: str) -> Iterable[str]:
        yield from self.splitter.split(data, do_paragraph_segmentation=False)
