
from backend.knowledge.parser.pdf_parser import load_doc
from backend.knowledge.weaviate.weaviate_handler import WeaviateHandler
from backend.knowledge.chunking.fixed_size import FixedChunking
import asyncio
from pydantic import BaseModel
from .get_url_data import crawl_content
from backend.app.core.config import settings
import sys
from fastapi import APIRouter

class Document(BaseModel):
    URI: str
    source: str

router = APIRouter()

def clean_data_from_url_scrapping(fetched_data):
    """
    {'statu'}
    """
    print(fetched_data)
    print(len(fetched_data))
    text = ""
    if (fetched_data is None) or (len(fetched_data) == 0) or ("content" not in fetched_data.keys()): return ""
    text = text + "\n" + fetched_data["content"]
    print(text)
    for children in fetched_data["children"]:
        text = text + "\n" + clean_data_from_url_scrapping(children)
    return text
    



@router.post("/ingestion")
async def ingest_weaviate(doc: Document):

    try:
        
        text = ""
        fetched_data = None
        if doc.source.lower() == "url":
            fetched_data =  await crawl_content(
                doc.URI,max_depth=settings.URL_PARSING_MAX_DEPT,
                skip_footer_header=True,skip_social_media=True
                )
            text = fetched_data["data"]["content"]
            for children in fetched_data["data"]["children"]:
                text = text + "\n" + clean_data_from_url_scrapping(children)
                
        elif (doc.source.lower() == "file") and ("pdf" in doc.URI.lower()):
           
            text = load_doc(doc.URI)
        else:
            return {"status": "fail", "data": "", "error": "URI not found"}
        # print(fetched_data)
        
        fixed_chunking = FixedChunking()
        chunks = await fixed_chunking.chunk(text)
        
        weaviate_handler = WeaviateHandler(weaviate_url=settings.WEAVIATE_URL,
            weaviate_api_key=settings.WEAVIATE_API_KEY,
            model_name=settings.EMBEDDING_MODEL,
            collection_name=settings.WEAVIATE_CLASS)
        weaviate_handler.upload_chunks_to_weaviate(source=doc.source,chunks=chunks)

        return {"status": "success", "data":"", "error":""}

    except Exception as e:
        print("=========== an exception has occured============")
        return {"status": "fail", "data": "", "error": e}


if __name__ == "__main__":
    # result1 = asyncio.run(ingest_weaviate({
    #     "URI": "backend/testdocs/test_invoice.pdf",
    #     "source": "file"
    # }))
    # if result1["status"] == "fail":
    #     print(result1)
    #     sys.exit(0)
    # print(result1)
    result2 = asyncio.run(ingest_weaviate({
        "URI": "https://www.iana.org/help/example-domains",
        "source": "url"
    }))
    print(result2)



