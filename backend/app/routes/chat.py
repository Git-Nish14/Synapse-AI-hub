from fastapi import APIRouter
from pydantic import BaseModel
from app.services.ai_providers import generate_chat_response

router = APIRouter()

class ChatRequest(BaseModel):
    prompt: str

@router.post("/chat")
async def chat(request: ChatRequest):
    response = await generate_chat_response(request.prompt)
    return {"provider": "Groq", "response": response}
