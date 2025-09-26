from fastapi import FastAPI
from pydantic import BaseModel
from backend.app.core.config import settings

app = FastAPI()

def create_router(app: FastAPI):
    from backend.app.api.chat_service import router as chat_router
    from backend.app.api.data_ingest import router as ingest_router
    from backend.app.api.retrieval import router as retrieval_router


    PREFIX_V1 = "/api/v1"

    app.include_router(chat_router, prefix=PREFIX_V1, tags=["Chat"])
    app.include_router(ingest_router, prefix=PREFIX_V1, tags=["Ingestion"])
    app.include_router(retrieval_router, prefix=PREFIX_V1, tags=["Retrieval"])

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
    )
    
    create_router(app)
    return app

app = create_app()

@app.get("/")
def base_url():
    return {"message": "Hey there ! I am ChatBot"}



