from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.ai_providers import AIProvider

router = APIRouter()
ai_provider = AIProvider()

class ImageRequest(BaseModel):
    prompt: str

@router.post("/image")
async def image(request: ImageRequest):
    result = await ai_provider.generate_image(request.prompt)

    if not result.get("success", False):
        raise HTTPException(status_code=400, detail=result.get("message", "Unknown error"))

    return {"provider": "ClipDrop", "image_base64": result["resultImage"]}
