from fastapi import FastAPI
from app.routes import chat, image
from app.routes import users
from app.routes import auth, credits  
from app.services.ai_providers import AIProvider
from app.db import models
from app.db.database import engine
from app.middleware.auth_middleware import AuthMiddleware
from app.routes import payments

app = FastAPI(title="Synapse AI Hub", version="1.0")
app.add_middleware(AuthMiddleware)


# Create tables automatically
models.Base.metadata.create_all(bind=engine)


# Initialize your AI provider
ai_provider = AIProvider()

# Register all routers
app.include_router(auth.router, tags=["Auth"])
app.include_router(users.router, tags=["Users"])
app.include_router(credits.router, prefix="/credits", tags=["Credits"])
app.include_router(chat.router, prefix="/api", tags=["Chat"])
app.include_router(image.router, prefix="/api", tags=["Image"])
app.include_router(payments.router)

# Handle shutdown events
@app.on_event("shutdown")
async def shutdown_event():
    await ai_provider.close()
