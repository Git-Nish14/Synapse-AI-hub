from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.ai_providers import generate_image

router = APIRouter()

class ImageRequest(BaseModel):
    prompt: str

@router.post("/image")
async def image(request: ImageRequest):
    result = await generate_image(request.prompt)

    if not result.get("success", False):
        raise HTTPException(status_code=400, detail=result.get("message", "Unknown error"))

    # Use the correct key from generate_image
    return {"provider": "ClipDrop", "image_base64": result["resultImage"]}
