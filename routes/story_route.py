from fastapi import APIRouter, Form, HTTPException
from services.story_tool import get_story_chain
from services.text_to_voice import text_to_voice
from supabase_client import supabase
import base64

router = APIRouter()

@router.post("/generate-story")
async def generate_story(
    user_id: str = Form(...),
    message: str = Form(...)
):
    try:
        # --- Validate user ---
        user_resp = supabase.table("users").select("*").eq("id", user_id).execute()
        if not user_resp.data:
            raise HTTPException(status_code=404, detail="User not found")

        # --- Fetch history ---
        history_resp = supabase.table("chat").select("role,message").eq("user_id", user_id).order("created_at").execute()
        history_text = "\n".join(
            [f"{'User' if m['role']=='user' else 'Assistant'}: {m['message']}" for m in history_resp.data]
        )

        # --- Generate Story ---
        story_chain = get_story_chain()
        story = story_chain.run({"history": history_text, "user_input": message})

        # --- Convert Story to Speech (Base64) ---
        audio_base64 = text_to_voice(story, lang="en")  # service returns base64

        # --- Save in tool_requests ---
        supabase.table("tool_requests").insert({
            "user_id": user_id,
            "tool_name": "story_generator",
            "input": message,
            "output": story
        }).execute()

        # --- Save chat history ---
        supabase.table("chat").insert([
            {"user_id": user_id, "role": "user", "message": message},
            {"user_id": user_id, "role": "assistant", "message": story}
        ]).execute()

        # --- Return JSON with both text + audio ---
        return {
            "story": story,
            "audio_base64": audio_base64
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
