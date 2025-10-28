import os
import httpx
import base64
from dotenv import load_dotenv

load_dotenv()

# ===== ENV KEYS =====
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
CLIPDROP_API_KEY = os.getenv("CLIPDROP_API")

# ===== DEFAULT MODELS =====
GROQ_DEFAULT_MODEL = "llama-3.1-8b-instant"


# ===== CHAT FUNCTION =====
async def generate_chat_response(prompt: str):
    """
    Sends a prompt to Groq API and returns the chat response.
    """
    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": GROQ_DEFAULT_MODEL,
        "messages": [{"role": "user", "content": prompt}]
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=data)

    if response.status_code != 200:
        return {"error": response.text}

    result = response.json()
    return {"provider": "Groq", "response": result["choices"][0]["message"]["content"]}


# ===== IMAGE FUNCTION =====
async def generate_image(prompt: str):
    """
    Sends a prompt to ClipDrop API to generate an image.
    Returns image as a base64 string.
    """
    if not prompt:
        return {"success": False, "message": "Prompt is required"}

    try:
        url = "https://clipdrop-api.co/text-to-image/v1"
        headers = {"x-api-key": CLIPDROP_API_KEY}

        # ClipDrop expects 'files' for the prompt
        files = {
            "prompt": (None, prompt, "text/plain")
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, files=files)

        if response.status_code != 200:
            return {"success": False, "message": response.text}

        # Convert raw image bytes to base64
        base64_image = base64.b64encode(response.content).decode("utf-8")
        result_image = f"data:image/png;base64,{base64_image}"

        return {
            "success": True,
            "message": "Image Generated",
            "resultImage": result_image
        }

    except Exception as e:
        return {"success": False, "message": str(e)}