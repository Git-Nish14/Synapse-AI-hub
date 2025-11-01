from fastapi import APIRouter
from pydantic import BaseModel
from app.services.ai_providers import AIProvider

router = APIRouter()
ai_provider = AIProvider()

class ChatRequest(BaseModel):
    prompt: str

@router.post("/chat")
async def chat(request: ChatRequest):
    return await ai_provider.generate_chat_response(request.prompt)
