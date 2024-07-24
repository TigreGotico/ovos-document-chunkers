from typing import Iterable, Dict, Optional

from ovos_document_chunkers.base import AbstractTextDocumentChunker
from quebra_frases import sentence_tokenize, paragraph_tokenize


class RegexSentenceSplitter(AbstractTextDocumentChunker):
    """
    A sentence splitter that uses regex-based tokenization.

    This splitter uses the `quebra_frases` library to tokenize paragraphs and sentences.

    Attributes:
        config (Dict): Configuration dictionary for the splitter.
    """

    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the splitter with a configuration.

        Args:
            config (Optional[Dict]): Configuration dictionary for the splitter.
                                     Defaults to an empty dictionary if None.
        """
        config = config or {}
        super().__init__(config)

    def chunk(self, data: str) -> Iterable[str]:
        """
        Split the input text into sentences.

        Args:
            data (str): The text to split.

        Returns:
            Iterable[str]: An iterable of sentences.
        """
        for c in data.split("\n"):
            for p in paragraph_tokenize(c):
                for s in sentence_tokenize(p):
                    yield s


class PySBDSentenceSplitter(AbstractTextDocumentChunker):
    """
    A sentence splitter that uses the PySBD library for sentence boundary detection.

    Attributes:
        config (Dict): Configuration dictionary for the splitter.
        splitter (pysbd.Segmenter): The PySBD segmenter instance.
    """

    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the splitter with a configuration.

        Args:
            config (Optional[Dict]): Configuration dictionary for the splitter.
                                     Defaults to {"lang": "en"} if None.
        """
        config = config or {"lang": "en"}
        super().__init__(config)
        import pysbd
        self.splitter = pysbd.Segmenter(language=self.config.get("lang", "en"), clean=False)

    def chunk(self, data: str) -> Iterable[str]:
        """
        Split the input text into sentences using PySBD.

        Args:
            data (str): The text to split.

        Returns:
            Iterable[str]: An iterable of sentences.
        """
        return self.splitter.segment(data)


class SaTSentenceSplitter(AbstractTextDocumentChunker):
    """
    A sentence splitter that uses the SaT library for sentence boundary detection.

    Attributes:
        config (Dict): Configuration dictionary for the splitter.
        model (str): The model name used by SaT.
        splitter (SaT): The SaT splitter instance.
    """

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

    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the splitter with a configuration.

        Args:
            config (Optional[Dict]): Configuration dictionary for the splitter.
                                     Defaults to {"model": "sat-3l-sm"} if None.
        """
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
        """
        Split the input text into sentences using SaT.

        Args:
            data (str): The text to split.

        Returns:
            Iterable[str]: An iterable of sentences.
        """
        yield from self.splitter.split(data, do_paragraph_segmentation=False)


class WtPSentenceSplitter(AbstractTextDocumentChunker):
    """
    A sentence splitter that uses the WtP library for sentence boundary detection.

    Attributes:
        config (Dict): Configuration dictionary for the splitter.
        model (str): The model name used by WtP.
        splitter (WtP): The WtP splitter instance.
    """

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

    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the splitter with a configuration.

        Args:
            config (Optional[Dict]): Configuration dictionary for the splitter.
                                     Defaults to {"model": "wtp-bert-mini"} if None.
        """
        config = config or {"model": "wtp-bert-mini"}
        super().__init__(config)
        from wtpsplit import WtP
        self.model = self.config["model"]
        assert self.model in self.VALID_MODELS

        cuda = self.config.get("use_cuda")
        if "bert" in self.model and self.config.get("use_onnx", True):  # use onnxruntime
            self.splitter = WtP(self.model, ort_providers=['CUDAExecutionProvider' if cuda else 'CPUExecutionProvider'])
        else:  # pytorch needed
            self.splitter = WtP(self.model)
            if cuda:
                self.splitter.half().to("cuda")

    def chunk(self, data: str) -> Iterable[str]:
        """
        Split the input text into sentences using WtP.

        Args:
            data (str): The text to split.

        Returns:
            Iterable[str]: An iterable of sentences.
        """
        yield from self.splitter.split(data, do_paragraph_segmentation=False)
