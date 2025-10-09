from langchain_openai import OpenAIEmbeddings
from typing import List, Dict, Any,Optional
from backend.app.core.config import settings
from .base import Embeddings

class OpenAIEmbedding(Embeddings):
    PROVIDER = "openai"
    def __init__(self, model: Optional[str]= None, api_key: Optional[str] = None):
        super().__init__(model or "text-embedding-3-large")
        self.model = model or "text-embedding-3-large"
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.embeddings = OpenAIEmbeddings(api_key=self.api_key,model=self.model)

    def get_embeddings(self, text: str):
        response = self.embeddings.embed_query(text=text)
        return response
    


if __name__ == "__main__":
    openaiemb = OpenAIEmbedding()
    result = openaiemb.get_embeddings("Hello this is law?")
    print(len(result))
    print(type(result))
    print(result)