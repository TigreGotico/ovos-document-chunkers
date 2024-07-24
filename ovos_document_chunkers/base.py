import abc
from typing import Iterable, Any, Dict


# TODO - once mature consider moving to ovos-plugin-manager-templates


class AbstractDocumentChunker:
    """
    An abstract base class for document chunkers.

    This class defines the interface for chunking documents into smaller text pieces.

    Attributes:
        config (Dict): Configuration dictionary for the chunker.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the chunker with a configuration.

        Args:
            config (Dict[str, Any]): Configuration dictionary for the chunker.
        """
        self.config = config

    @abc.abstractmethod
    def chunk(self, data: Any) -> Iterable[str]:
        """
        Chunk the given data into smaller pieces.

        This method must be implemented by subclasses.

        Args:
            data (Any): The data to chunk.

        Returns:
            Iterable[str]: An iterable of string chunks.
        """


class AbstractTextDocumentChunker(AbstractDocumentChunker):
    """
    An abstract base class for text document chunkers.

    This class extends the AbstractDocumentChunker to handle text documents.
    """

    @abc.abstractmethod
    def chunk(self, data: str) -> Iterable[str]:
        """
        Chunk the given text data into smaller pieces.

        This method must be implemented by subclasses.

        Args:
            data (str): The text data to chunk.

        Returns:
            Iterable[str]: An iterable of string chunks.
        """
