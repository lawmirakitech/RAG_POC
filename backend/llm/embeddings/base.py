from abc import ABC, abstractmethod
from typing import Optional
from backend.app.core.config import settings
class Embeddings(ABC):

    def __init__(self, model: Optional[str] = None):
        model = settings.EMBEDDING_MODEL
    @abstractmethod
    def get_embeddings(self, text: str):
        pass