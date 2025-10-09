from .base import Embeddings
from typing import Dict, Type, List, Any
from dataclasses import dataclass
from .openai_embeddings import OpenAIEmbedding
from .sentencetransformer_embeddings import SentenceTransformerEmbeddings
# from backend.app.core.config import settings

PROVIDERS: Dict[str, Type[Embeddings]] = {
    OpenAIEmbedding.PROVIDER: OpenAIEmbedding,
    SentenceTransformerEmbeddings.PROVIDER: SentenceTransformerEmbeddings,
}

@dataclass
class Providerparams:
    api_key: str = None
    api_base_url: str = None

def get_embedding_service(provider: str, model: str, params: Providerparams=None) -> Embeddings:
    provider = provider.lower()
    if provider not in PROVIDERS:
        raise ValueError(f"Unsupported provider: {provider}")
    print(f"======== provider = {provider}===============")
    if provider == "openai":
        return OpenAIEmbedding(model=model, api_key=params.api_key)
    elif provider == "sentence-transformer":
        return SentenceTransformerEmbeddings(tokenizer=model, model=model)


def get_default_embedding_service() -> Embeddings:
    """Get the default embedding service based on configuration settings."""
    from backend.app.core.config import settings
    
    provider = settings.DEFAULT_EMBEDDING_PROVIDER.lower()
    model = settings.DEFAULT_EMBEDDING_MODEL
    
    # Create appropriate params based on provider
    params = None
    if provider == "openai":
        params = Providerparams(
            api_key=settings.OPENAI_API_KEY,
            api_base_url=settings.OPENAI_API_BASE
        )
    
    return get_embedding_service(provider, model, params)


if __name__ == "__main__":

    obj = get_default_embedding_service()
    result = obj.get_embeddings("how are you law?")
    print(type(obj))
    print(type(result))
    print(len(result))
    print(result)