# routes/image_caption_routes.py
from fastapi import APIRouter, UploadFile, File
from services.content_tool import generate_caption_google
import json

router = APIRouter(prefix="/image-caption", tags=["Image Caption"])

@router.post("/")
async def caption_image(image: UploadFile = File(...)):
    result = await generate_caption_google(image)

    # Gemini response JSON string ko dict me convert karna
    try:
        return json.loads(result)
    except:
        return {"raw_output": result}
