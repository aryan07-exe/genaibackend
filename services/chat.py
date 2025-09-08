from datetime import datetime
from langchain_google_genai import ChatGoogleGenerativeAI
from supabase_client import supabase  # import your client
from uuid import UUID

# initialize LLM
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.7)

# ------------------ CHAT HISTORY ------------------
def get_chat_history(user_id: UUID, limit: int = 10):
    response = (
        supabase.table("chat")
        .select("*")
        .eq("user_id", str(user_id))  # UUID stored as string in Supabase
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    data = response.data or []
    return list(reversed(data))  # oldest first


# ------------------ SAVE MESSAGE ------------------
def save_message(user_id: UUID, role: str, content: str):
    response = supabase.table("chat").insert(
        {
            "user_id": str(user_id),
            "role": role,
            "message": content,
            "created_at": datetime.utcnow().isoformat(),
        }
    ).execute()
    return response.data


# ------------------ USER PROFILE ------------------
def get_user_profile(user_id: UUID):
    response = supabase.table("users").select("*").eq("id", str(user_id)).single().execute()
    return response.data


# ------------------ LLM RESPONSE ------------------
def extract_text(response):
    """Extract plain text string from LLM response."""
    if isinstance(response.content, str):
        return response.content
    elif isinstance(response.content, list):
        return " ".join(
            part.get("text", "") if isinstance(part, dict) else str(part)
            for part in response.content
        )
    else:
        return str(response.content)


def chat_with_llm(user_id: UUID, user_message: str):
    # fetch user profile
    user_profile = get_user_profile(user_id)

    # fetch recent chat history
    history = get_chat_history(user_id)

    # build system prompt with user profile context
    if user_profile:
        system_prompt = (
            f"You are the master of the user's art. "
            f"Understand their style, preferences, and guide them thoughtfully. "
            f"Always respond with expertise and context awareness.\n\n"
            f"User Profile:\n"
            f"Name: {user_profile.get('name')}\n"
            f"Craft: {user_profile.get('craft')}\n"
            f"Location: {user_profile.get('location')}\n"
            f"Experience: {user_profile.get('experience')}\n\n"
            f"IMPORTANT INSTRUCTION: "
            f"Respond only in plain text sentences. "
            f"Do not use bullet points, numbers, bold, markdown, or special characters. "
            f"Just return a clean string."
        )
    else:
        system_prompt = "You are the master of the user's art. Respond thoughtfully."

    # construct messages for LLM
    messages = [{"role": "system", "content": system_prompt}]

    for msg in history:
        messages.append({"role": msg["role"], "content": msg["message"]})

    messages.append({"role": "user", "content": user_message})

    # call Gemini API via LangChain
    response = llm.invoke(messages)
    reply_text = extract_text(response)

    # save both user + assistant messages
    save_message(user_id, "user", user_message)
    save_message(user_id, "assistant", reply_text)

    return reply_text
