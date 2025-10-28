from fastapi import FastAPI
from app.routes import chat, image

app = FastAPI()

app.include_router(chat.router, prefix="/api")
app.include_router(image.router, prefix="/api")


