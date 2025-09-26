from backend.knowledge.weaviate.weaviate_handler import WeaviateHandler
from ..core.config import settings
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class query(BaseModel):
    query: str

@router.get("/retrieve")
def retrieve(query):
    weaviate_hander = WeaviateHandler(weaviate_url=settings.WEAVIATE_URL,
            weaviate_api_key=settings.WEAVIATE_API_KEY,
            model_name=settings.EMBEDDING_MODEL,
            collection_name="ChatDemo")
    return weaviate_hander.retriver(query["query"])


if __name__ == "__main__":
    text = retrieve("Government of Himachal Pradesh")
    print(text)