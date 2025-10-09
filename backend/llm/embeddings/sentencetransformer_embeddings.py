from transformers import AutoModel, AutoTokenizer
import torch
from backend.app.core.config import settings
from .base import Embeddings

class SentenceTransformerEmbeddings(Embeddings):

    PROVIDER = "sentence-transformer"
    
    def __init__(self, tokenizer = None, model = None):
        super().__init__(model or settings.EMBEDDING_MODEL)
        self.tokenizer = AutoTokenizer.from_pretrained(tokenizer or settings.EMBEDDING_MODEL)
        self.model = AutoModel.from_pretrained(model or settings.EMBEDDING_MODEL)
        

    def get_embeddings(self,text: str):
        inputs = self.tokenizer(text, return_tensors="pt")
        with torch.no_grad():
            embeddings = self.model(**inputs)[0].mean(dim=1)

        
        return embeddings.numpy().flatten().tolist()
    


if __name__ == "__main__":
    
    tokenizer = "BAAI/bge-large-en-v1.5"
    model = "BAAI/bge-large-en-v1.5"

    embeddings = SentenceTransformerEmbeddings(tokenizer=tokenizer, model=model)
    
    result = embeddings.get_embeddings("Hello this is law?")
    # result = embedding.flatten().tolist()
    print(len(result))
    print(type(result))
    print(result)