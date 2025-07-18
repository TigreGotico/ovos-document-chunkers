from typing import Iterable, Dict, Optional

from ovos_document_chunkers.base import AbstractTextDocumentChunker
from ovos_document_chunkers.text.sentence import WtPSentenceSplitter, SaTSentenceSplitter
from quebra_frases import paragraph_tokenize


class RegexParagraphSplitter(AbstractTextDocumentChunker):
    """
    A paragraph splitter that uses regex-based tokenization.

    This splitter uses the `quebra_frases` library to tokenize paragraphs.

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
        Split the input text into paragraphs.

        Args:
            data (str): The text to split.

        Returns:
            Iterable[str]: An iterable of paragraphs.
        """
        for c in data.split("\n\n"):
            if not c.strip():
                continue
            try:
                for p in paragraph_tokenize(c):
                    yield p
            except:
                yield c

class WtPParagraphSplitter(WtPSentenceSplitter):
    """
    A paragraph splitter that uses the WtP library for paragraph boundary detection.

    This class extends the WtPSentenceSplitter to perform paragraph splitting.
    """

    def chunk(self, data: str) -> Iterable[str]:
        """
        Split the input text into sentences using WtP.

        Args:
            data (str): The text to split.

        Returns:
            Iterable[str]: An iterable of sentences.
        """
        for chunk in self.splitter.split(data, do_paragraph_segmentation=True):
            if isinstance(chunk, list):
                for c in chunk:
                    yield c
            else:
                yield chunk


class SaTParagraphSplitter(SaTSentenceSplitter):
    """
    A paragraph splitter that uses the SaT library for paragraph boundary detection.

    This class extends the SaTSentenceSplitter to perform paragraph splitting.
    """

    def chunk(self, data: str) -> Iterable[str]:
        """
        Split the input text into paragraphs using SaT.

        Args:
            data (str): The text to split.

        Returns:
            Iterable[str]: An iterable of paragraphs.
        """
        yield from self.splitter.split(data, do_paragraph_segmentation=True)
