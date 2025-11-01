import os
import base64
import logging
import httpx
from dotenv import load_dotenv
from typing import Dict, Any

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
CLIPDROP_API_KEY = os.getenv("CLIPDROP_API_KEY")

if not GROQ_API_KEY or not CLIPDROP_API_KEY:
    raise RuntimeError("❌ Missing required API keys (GROQ_API_KEY / CLIPDROP_API_KEY).")

logger = logging.getLogger("ai_providers")
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(levelname)s] %(message)s")

GROQ_DEFAULT_MODEL = "llama-3.1-8b-instant"


class AIProvider:
    """
    Secure, async, high-performance integration with Groq and ClipDrop APIs.
    """

    def __init__(self):
        self.groq_api_key = GROQ_API_KEY
        self.clipdrop_api_key = CLIPDROP_API_KEY
        self.groq_model = GROQ_DEFAULT_MODEL

        self._groq_client = httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {self.groq_api_key}",
                "Content-Type": "application/json"
            },
            timeout=httpx.Timeout(30.0, read=60.0)
        )
        self._clipdrop_client = httpx.AsyncClient(
            headers={"x-api-key": self.clipdrop_api_key},
            timeout=httpx.Timeout(30.0, read=60.0)
        )

        logger.info("✅ AIProvider initialized successfully.")

    async def close(self):
        await self._groq_client.aclose()
        await self._clipdrop_client.aclose()
        logger.info("🧹 AIProvider clients closed cleanly.")

    async def generate_chat_response(self, prompt: str) -> Dict[str, Any]:
        if not prompt:
            return {"error": "Prompt is required"}

        url = "https://api.groq.com/openai/v1/chat/completions"
        payload = {"model": self.groq_model, "messages": [{"role": "user", "content": prompt}]}

        try:
            response = await self._groq_client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            return {"provider": "Groq", "response": content}
        except Exception as e:
            logger.error(f"Groq API error: {e}")
            return {"error": str(e)}

    async def generate_image(self, prompt: str) -> Dict[str, Any]:
        if not prompt:
            return {"success": False, "message": "Prompt is required"}

        url = "https://clipdrop-api.co/text-to-image/v1"
        files = {"prompt": (None, prompt, "text/plain")}

        try:
            response = await self._clipdrop_client.post(url, files=files)
            response.raise_for_status()
            base64_image = base64.b64encode(response.content).decode("utf-8")
            return {
                "success": True,
                "message": "Image generated successfully",
                "resultImage": f"data:image/png;base64,{base64_image}"
            }
        except Exception as e:
            logger.error(f"ClipDrop API error: {e}")
            return {"success": False, "message": str(e)}
