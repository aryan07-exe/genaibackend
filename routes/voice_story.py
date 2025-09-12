from fastapi import APIRouter, Form, HTTPException
from services.story_tool import get_story_chain
from services.text_to_voice import text_to_voice
from supabase_client import supabase

router = APIRouter()

@router.post("/generate-story")
async def generate_story(
    user_id: str = Form(...),
    message: str = Form(...),
):
    try:
        # --- Step 1: Validate user ---
        user_resp = supabase.table("users").select("*").eq("id", user_id).execute()
        if not user_resp.data:
            raise HTTPException(status_code=404, detail="User not found")

        # --- Step 2: Fetch history for context ---
        history_resp = supabase.table("chat").select("role,message").eq("user_id", user_id).order("created_at").execute()
        history_data = history_resp.data

        history_text = ""
        for msg in history_data:
            role = "User" if msg["role"] == "user" else "Assistant"
            history_text += f"{role}: {msg['message']}\n"

        # --- Step 3: Generate Story ---
        story_chain = get_story_chain()
        story = story_chain.run({
            "history": history_text,
            "user_input": message
        })

        # --- Step 4: Convert Story → Speech ---
        story_audio = text_to_voice(story, lang="en")

        # --- Step 5: Save in tool_requests ---
        supabase.table("tool_requests").insert({
            "user_id": user_id,
            "tool_name": "story_generator",
            "input": message,
            "output": story
        }).execute()

        # --- Step 6: Save chat (user + assistant) ---
        supabase.table("chat").insert([
            {
                "user_id": user_id,
                "role": "user",
                "message": message
            },
            {
                "user_id": user_id,
                "role": "assistant",
                "message": story
            }
        ]).execute()

        # --- Step 7: Fetch updated history ---
        updated_history = supabase.table("chat").select("*").eq("user_id", user_id).order("created_at").execute()

        return {
            "story_text": story,
            "story_audio": story_audio,   # base64 string
            "history": updated_history.data
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
