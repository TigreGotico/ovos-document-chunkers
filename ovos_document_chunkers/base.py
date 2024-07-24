import abc
from typing import Iterable, Any, Dict

# TODO - once mature consider moving to ovos-plugin-manager-templates


class AbstractDocumentChunker:
    def __init__(self, config: Dict):
        self.config = config

    @abc.abstractmethod
    def chunk(self, data: Any) -> Iterable[str]:
        pass


class AbstractTextDocumentChunker(AbstractDocumentChunker):

    @abc.abstractmethod
    def chunk(self, data: str) -> Iterable[str]:
        pass
