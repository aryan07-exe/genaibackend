from sqlalchemy.orm import Session
from models import ChatMessage, User
from datetime import datetime
from langchain_google_genai import ChatGoogleGenerativeAI  # or whichever LLM wrapper you're using
from uuid import UUID

# initialize LLM
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.7)

def get_chat_history(db: Session, user_id: UUID, limit: int = 10):
    return (
        db.query(ChatMessage)
        .filter_by(user_id=user_id)
        .order_by(ChatMessage.created_at.desc())
        .limit(limit)
        .all()
    )[::-1]  # reverse → oldest first

def save_message(db: Session, user_id: UUID, role: str, content: str):
    msg = ChatMessage(
        user_id=user_id, role=role, message=content
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg

def extract_text(response):
    """Extract plain text string from LLM response."""
    if isinstance(response.content, str):
        return response.content
    elif isinstance(response.content, list):
        # sometimes it's a list of dicts like [{'type': 'text', 'text': '...'}]
        return " ".join(
            part.get("text", "") if isinstance(part, dict) else str(part)
            for part in response.content
        )
    else:
        return str(response.content)
    
def get_user_profile(db: Session, user_id: UUID):
    """Fetch actual user profile from DB"""
    return db.query(User).filter(User.id == user_id).first()

def chat_with_llm(db: Session, user_id: UUID, user_message: str):
    # fetch user profile
    user_profile = get_user_profile(db, user_id)

    # fetch recent chat history
    history = get_chat_history(db, user_id)

    # build system prompt with actual values from `users` table
    if user_profile:
        system_prompt = (
    f"You are the master of the user's art. "
    f"Understand their style, preferences, and guide them thoughtfully. "
    f"Always respond with expertise and context awareness.\n\n"
    f"User Profile:\n"
    f"Name: {user_profile.name}\n"
    f"Craft: {user_profile.craft}\n"
    f"Location: {user_profile.location}\n"
    f"Experience: {user_profile.experience}\n\n"
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
        messages.append({"role": msg.role, "content": msg.message})

    messages.append({"role": "user", "content": user_message})

    # call LLM
    response = llm.invoke(messages)
    reply_text = extract_text(response)

    # save both messages
    save_message(db, user_id, "user", user_message)
    save_message(db, user_id, "assistant", reply_text)

    return reply_text
    
