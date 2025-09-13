# tools/image_caption_tool.py
import google.generativeai as genai
from fastapi import UploadFile
import io
from PIL import Image
import os
from dotenv import load_dotenv

load_dotenv()

my_api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=my_api_key)

model = genai.GenerativeModel("gemini-2.5-flash")  # ya "gemini-pro-vision" agar available hai

async def generate_caption_google(image: UploadFile):
    try:
        # Image ko PIL format me convert karna
        img_bytes = await image.read()
        pil_image = Image.open(io.BytesIO(img_bytes))

        # Prompt with variations
        response = model.generate_content(
            [
                """You are an expert photo captioning assistant. 
                Generate 3 types of captions for this image:
                1. Short (one line, simple).
                2. Medium (2–3 lines, descriptive).
                3. Long (detailed narrative style).
                Also, provide a short analysis of the scene (labels, description, and if anything unsafe).
                Return JSON strictly in this format:
                {
                    "captions": {
                        "short": "...",
                        "medium": "...",
                        "long": "..."
                    },
                    "analysis": {
                        "labels": ["..."],
                        "description": "...",
                        "safe_search": { }
                    }
                }""",
                pil_image
            ]
        )

        return response.candidates[0].content.parts[0].text.strip()

    except Exception as e:
        return {"error": str(e)}
