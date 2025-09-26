
import weaviate
from weaviate.classes.config import Configure, Property, DataType
from weaviate.classes.init import Auth
from weaviate.classes.query import Filter
import logging
from typing import List,Optional, Dict, Any
from backend.llm.embeddings.embeddings import Embeddings
from backend.app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WeaviateHandler:
    def __init__(self, 
                 weaviate_url: str,
                 weaviate_api_key: str,
                 model_name: str = settings.EMBEDDING_MODEL,
                 collection_name: str = "DocumentChunks"):
        """
        Initialize the pipeline
        
        Args:
            weaviate_url: Weaviate Cloud instance URL
            weaviate_api_key: API key for authentication
            model_name: Sentence transformer model name
            collection_name: Name of the Weaviate collection
        """
        self.weaviate_url = weaviate_url
        self.weaviate_api_key = weaviate_api_key
        self.model_name = model_name
        self.collection_name = collection_name
        self.embedding = Embeddings()
        self.client = self._initialize_weaviate_client()
        self._setup_collection_schema()

    def _setup_collection_schema(self):
        """Create or verify the collection schema in Weaviate"""
        try:
            # Check if collection exists
            if self.client.collections.exists(self.collection_name):
                logger.info(f"Collection '{self.collection_name}' already exists")
                self.collection = self.client.collections.get(self.collection_name)
            else:
                # Create new collection with schema
                logger.info(f"Creating new collection: {self.collection_name}")
                self.collection = self.client.collections.create(
                    name=self.collection_name,
                    properties=[
                                    Property(name="document_id", data_type=DataType.TEXT),
                                    Property(name="source_uri", data_type=DataType.TEXT),
                                    Property(name="project_id", data_type=DataType.TEXT),
                                    Property(name="tenant_id", data_type=DataType.TEXT),
                                    Property(name="user_id", data_type=DataType.TEXT),
                                    Property(name="tags", data_type=DataType.TEXT_ARRAY),
                                    Property(name="content", data_type=DataType.TEXT),
                                    Property(name="chunk_index", data_type=DataType.INT),
                                    Property(name="page_number", data_type=DataType.INT),
                                    Property(name="created_at", data_type=DataType.DATE),
                                ],
                    # Configure vectorization
                    vectorizer_config=Configure.Vectorizer.none(),  # We'll provide our own vectors
                )
                logger.info(f"Collection '{self.collection_name}' created successfully")
                
        except Exception as e:
            logger.error(f"Error setting up collection schema: {e}")
            raise
        
    def _initialize_weaviate_client(self) -> weaviate.WeaviateClient:
        """Initialize Weaviate client with authentication"""
        try:
            client = weaviate.connect_to_weaviate_cloud(
                cluster_url=self.weaviate_url,
                auth_credentials=Auth.api_key(self.weaviate_api_key),
            )
            logger.info("Successfully connected to Weaviate Cloud")
            return client
        except Exception as e:
            logger.error(f"Failed to connect to Weaviate: {e}")
            raise
            
    def upload_chunks_to_weaviate(self,source ,chunks: List[str], batch_size: int = 50):

        total_chunks = len(chunks)
        print(f"Starting upload of {total_chunks} chunks to '{self.collection_name}' collection...")

        # Get the collection
        collection = self.client.collections.get(self.collection_name)

        # Process chunks in batches
        for i in range(0, total_chunks, batch_size):
            batch_chunks = chunks[i:i + batch_size]

            try:
                # Prepare batch data
                batch_objects = []

                for idx, chunk in enumerate(batch_chunks):
                    # Generate embedding for the chunk
                    embedding = self.embedding.get_embeddings(chunk)

                    # Create data object with properties and vector
                    data_object = {
                        "content": chunk,
                        "chunk_id": i + idx,
                        "source": source,  # You can modify this
                        "chunk_size": len(chunk)
                    }

                    batch_objects.append(
                        collection.data.insert(
                            properties=data_object,
                            vector=embedding.flatten().tolist(),

                        )
                    )

                print(f"✓ Uploaded batch {i//batch_size + 1}/{(total_chunks-1)//batch_size + 1} "
                    f"(chunks {i+1}-{min(i+batch_size, total_chunks)})")

            except Exception as e:
                print(f"✗ Error uploading batch {i//batch_size + 1}: {e}")
                continue

        print(f"Upload complete! Total chunks processed: {total_chunks}")

    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection"""
        try:
            aggregate_result = self.collection.aggregate.over_all(
                total_count=True
            )
            
            return {
                "total_documents": aggregate_result.total_count,
                "collection_name": self.collection_name,
                "model_name": self.model_name
            }
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {}
        
    def retriver(self,query):

        # Perform vector search
        collection = self.client.collections.get(str(self.collection_name))
        query_embeddings = self.embedding.get_embeddings(query).tolist()[0]
        response = self._vector_search(collection, query_embeddings)
        data=[{"uuid": o.uuid, "properties": o.properties} for o in response.objects]
        source=data[0]['properties']['source']
        return data,source
    
    def _vector_search(self,collection, query_embedding):
        # print(f"============{query_embedding}==========")
        response = collection.query.near_vector(
            near_vector=query_embedding,
            limit=3,
            return_metadata=["distance"],
            return_properties=["content", "chunk_id", "source"]
        )
        return response
    

    def close(self):
        """Close the Weaviate client connection"""
        if self.client:
            self.client.close()
            logger.info("Weaviate client connection closed")


if __name__ == "__main__":

    weaviatehandler = WeaviateHandler(weaviate_url=settings.WEAVIATE_URL,
            weaviate_api_key=settings.WEAVIATE_API_KEY,
            model_name=settings.EMBEDDING_MODEL,
            collection_name="ChatDemo")
    
    # weaviatehandler.upload_chunks_to_weaviate("test", ["Law did it"])
    text = weaviatehandler.retriver("Law")
    print(f"==========={text}===========")

    
        