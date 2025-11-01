from fastapi import FastAPI
from app.routes import chat, image
from app.services.ai_providers import AIProvider

app = FastAPI(title="Synapse AI Hub", version="1.0")

ai_provider = AIProvider()

app.include_router(chat.router, prefix="/api", tags=["Chat"])
app.include_router(image.router, prefix="/api", tags=["Image"])

@app.on_event("shutdown")
async def shutdown_event():
    await ai_provider.close()
