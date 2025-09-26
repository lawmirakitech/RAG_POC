from fastapi import APIRouter
from pydantic import BaseModel
from backend.llm.chat.chat_bot import chat_bot



class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    answer: str
    source: str

router = APIRouter()



@router.post("/chat",response_model=ChatResponse)
def chat(query: ChatRequest):
    response = chat_bot.chat(query.question)
    # response = ("hello","test")
    return {
        "answer": str(response[0]),
        "source": str(response[1])
    }