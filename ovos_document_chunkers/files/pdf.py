from typing import Iterable, Optional, List, Dict

import requests
from ovos_document_chunkers.base import AbstractTextDocumentChunker


class PDFSentenceSplitter(AbstractTextDocumentChunker):
    """
    A sentence splitter for PDF documents.

    This splitter breaks down PDF documents into sentences.

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
        self.splitter = PDFParagraphSplitter(self.config)

    def chunk(self, data: str) -> Iterable[str]:
        """
        Split the input PDF text into sentences.

        Args:
            data (str): The PDF text to split.

        Returns:
            Iterable[str]: An iterable of sentences that are derived from the PDF text.
        """
        for chunk in self.splitter.chunk(data):
            for p in chunk.split("\n"):
                if len(p.split()) > 3:
                    yield p.strip()


class PDFParagraphSplitter(AbstractTextDocumentChunker):
    """
    A paragraph splitter for PDF documents.

    This splitter breaks down PDF documents into paragraphs.

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
        Split the input PDF text into paragraphs.

        Args:
            data (str): The PDF text to split.

        Returns:
            Iterable[str]: An iterable of paragraphs extracted from the PDF text.
        """
        for chunk in parse_pdf(data):
            yield chunk


def parse_pdf(path: str,
              bad_words: Optional[List[str]] = None,
              stop_words: Optional[List[str]] = None,
              min_words: int = 5) -> Iterable[str]:
    """
    Extract and parse text from a PDF file, filtering out unwanted content.

    This function processes the PDF file at the given path, removing specified
    bad words and stop words, and ensuring that the resulting chunks meet
    a minimum word count.

    Args:
        path (str): The file path to the PDF document.
        bad_words (Optional[List[str]]): A list of words that, if found,
                                          will cause the chunk to be discarded.
                                          Defaults to an empty list.
        stop_words (Optional[List[str]]): A list of words to ignore in the word count.
                                           Defaults to an empty list.
        min_words (int): The minimum number of words a chunk must contain
                         to be yielded. Defaults to 5.

    Returns:
        Iterable[str]: An iterable of cleaned text chunks extracted from the PDF.
    """
    if path.startswith("http"):
        response = requests.get(path)
        response.raise_for_status()  # Raise an error for bad status codes
        path = response.text
    import textract

    # Default values for bad_words and stop_words
    bad_words = bad_words or []
    # ignore in word count
    stop_words = stop_words or []

    text = textract.process(path, extension='pdf', encoding='utf-8').decode("utf-8")

    for chunk in text.split("\n\n"):
        words = [w for w in chunk.split() if w.lower() not in stop_words and len(w) > 3]
        lnorm = " ".join(words)
        if any([w in chunk.lower() for w in bad_words]):
            continue
        elif len(lnorm.split()) < min_words:
            continue
        yield chunk.strip()


if __name__ == "__main__":
    pdf_path = "/ovos-document-chunkers/The Complete Works of H.P. Lovecraft.pdf"

    chunker = PDFParagraphSplitter()
    # chunker = PDFSentenceSplitter()

    i = 0
    for chunk in chunker.chunk(pdf_path):
        print("### chunk:", i, chunk.replace("\n", "  "))
        i += 1
