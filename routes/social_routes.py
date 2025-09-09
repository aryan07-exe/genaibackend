from fastapi import APIRouter, Form, File, UploadFile, HTTPException
import os
from uuid import UUID
from datetime import datetime
from supabase_client import supabase
from workflow.social_agent import run_social_agent

router = APIRouter()

# Optional: keep uploaded files if you want debugging
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/assistant/social")
async def social_media_chat(
    user_id: UUID = Form(...),
    query: str = Form(None),
    image: UploadFile = File(None),
):
    """
    Endpoint for AI social media assistant.
    Accepts either:
      - text only
      - image only
      - both text + image
    """

    input_data = {}

    # 🟢 Handle image upload
    if image:
        try:
            file_bytes = await image.read()
            if not file_bytes:
                raise HTTPException(status_code=400, detail="Uploaded image is empty.")

            input_data["image_bytes"] = file_bytes

            # (Optional) Save to disk for logging/debugging
            save_path = os.path.join(UPLOAD_DIR, image.filename)
            with open(save_path, "wb") as f:
                f.write(file_bytes)

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

    # 🟢 Handle text input
    if query:
        input_data["text"] = query.strip()

    if not input_data:
        raise HTTPException(status_code=400, detail="Please provide either text or an image.")

    # 🟢 Run AI agent
    try:
        response = run_social_agent(input_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI agent error: {str(e)}")

    # 🟢 Log user message in Supabase
    try:
        supabase.table("chat").insert({
            "user_id": str(user_id),
            "role": "user",
            "message": query if query else f"[image: {image.filename}]",
            "created_at": datetime.utcnow().isoformat(),
        }).execute()

        supabase.table("chat").insert({
            "user_id": str(user_id),
            "role": "assistant",
            "message": response,
            "created_at": datetime.utcnow().isoformat(),
        }).execute()
    except Exception as e:
        # Don’t block the response if DB insert fails
        print(f"⚠️ Failed to save chat logs: {e}")

    return {"response": response}
