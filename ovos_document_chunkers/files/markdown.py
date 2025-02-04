import os.path
from typing import Iterable, Tuple, Dict, Optional
import requests
from ovos_document_chunkers.base import AbstractTextDocumentChunker


class MarkdownSentenceSplitter(AbstractTextDocumentChunker):
    """
    A sentence splitter for markdown documents.

    This splitter breaks down markdown documents into sentences.

    Attributes:
        config (Dict): Configuration dictionary for the splitter.
        splitter (MarkdownParagraphSplitter): Instance of MarkdownParagraphSplitter to handle paragraph splitting.
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
        self.splitter = MarkdownParagraphSplitter(self.config)

    def chunk(self, data: str) -> Iterable[str]:
        """
        Split the input markdown text into sentences.

        Args:
            data (str): The markdown text to split.

        Returns:
            Iterable[str]: An iterable of sentences.
        """
        for chunk in self.splitter.chunk(data, include_title=False):
            for p in chunk.split("\n"):
                if p:
                    yield p.strip()


class MarkdownParagraphSplitter(AbstractTextDocumentChunker):
    """
    A paragraph splitter for markdown documents.

    This splitter breaks down markdown documents into paragraphs.

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

    def chunk(self, data: str, include_title: bool = True) -> Iterable[str]:
        """
        Split the input markdown text into paragraphs.

        Args:
            data (str): The markdown text to split.
            include_title (bool): Whether to include the title in the paragraphs. Defaults to True.

        Returns:
            Iterable[str]: An iterable of paragraphs.
        """
        if data.startswith("http"):
            response = requests.get(data)
            response.raise_for_status()  # Raise an error for bad status codes
            data = response.text
        if os.path.isfile(data) and data.endswith(".md"):
            with open(data) as f:
                data = f.read()
        import markdown_to_json
        raw = markdown_to_json.dictify(data)

        for k2, chunk in _parse_dict("", raw):
            if include_title:
                yield f"{k2}\n\n{chunk}"
            else:
                yield chunk


def _parse_dict(k: str, d: Dict, skip_lists: bool = True) -> Iterable[Tuple[str, str]]:
    """
    Parse a dictionary and yield key-chunk pairs.

    Args:
        k (str): The current key prefix.
        d (Dict): The dictionary to parse.
        skip_lists (bool): Whether to skip lists in the dictionary. Defaults to True.

    Returns:
        Iterable[Tuple[str, str]]: An iterable of key-chunk pairs.
    """
    for k2, v in d.items():
        if isinstance(v, dict):
            for k3, chunk in _parse_dict(k2, v):
                yield f"{k} - {k3}", chunk
        elif isinstance(v, list):
            if skip_lists:
                continue
            for k3, chunk in _parse_list(k2, v):
                yield f"{k} - {k3}", chunk
        elif isinstance(v, str):
            for k3, chunk in _parse_txt(k2, v):
                yield f"{k} - {k3}", chunk


def _parse_list(k: str, d: list) -> Iterable[Tuple[str, str]]:
    """
    Parse a list and yield key-chunk pairs.

    Args:
        k (str): The current key prefix.
        d (list): The list to parse.

    Returns:
        Iterable[Tuple[str, str]]: An iterable of key-chunk pairs.
    """
    for k2, v in enumerate(d):
        if isinstance(v, dict):
            for k3, chunk in _parse_dict(k, v):
                yield f"{k} - {k3}", chunk
        elif isinstance(v, list):
            for k3, chunk in _parse_list(k, v):
                yield f"{k} - {k3}", chunk
        elif isinstance(v, str):
            for k3, chunk in _parse_txt(k2, v):
                yield f"{k} - {k3}", chunk


def _parse_txt(k: str, d: str) -> Iterable[Tuple[str, str]]:
    """
    Parse a text and yield key-chunk pairs.

    Args:
        k (str): The current key prefix.
        d (str): The text to parse.

    Returns:
        Iterable[Tuple[str, str]]: An iterable of key-chunk pairs.
    """
    for chunk in [d.strip()]:
        if "</details>" in chunk:
            for c in chunk.split("</details>"):
                for c2 in c.split("<details>"):
                    c2 = c2.replace("[", "").replace("]", "").strip()
                    if c2:
                        yield k, c2
            continue
        yield k, chunk.replace("[", "").replace("]", "").strip()


if __name__ == "__main__":
    import requests

    chunker = MarkdownSentenceSplitter()
    chunker = MarkdownParagraphSplitter()
    for chunk in chunker.chunk("https://github.com/OpenVoiceOS/ovos-core/raw/dev/README.md"):
        print(chunk)
