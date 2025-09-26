from transformers import AutoModel, AutoTokenizer
import torch
from backend.app.core.config import settings

class Embeddings:

    def __init__(self, tokenizer = None, model = None):
        self.tokenizer = AutoTokenizer.from_pretrained(settings.EMBEDDING_MODEL)
        self.model = AutoModel.from_pretrained(settings.EMBEDDING_MODEL)

    def get_embeddings(self,text):
        inputs = self.tokenizer(text, return_tensors="pt")
        with torch.no_grad():
            embeddings = self.model(**inputs)[0].mean(dim=1)
        return embeddings.numpy()
    


if "__name__" == "__main__":

    tokenizer = AutoTokenizer.from_pretrained("BAAI/bge-large-en-v1.5")
    model = AutoModel.from_pretrained("BAAI/bge-large-en-v1.5")

    embeddings = Embeddings(tokenizer=tokenizer, model=model)