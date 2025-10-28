from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def auth_home():
    return {"message": "Auth route working!"}
