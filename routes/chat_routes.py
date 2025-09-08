from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
 
from services.chat import chat_with_llm
from uuid import UUID
router = APIRouter()

@router.post("/{user_id}")
def chat(user_id: UUID, message: str):
    """
    Handles chat for a given user_id.
    Loads chat history, prepends system prompt, calls LLM, 
    saves both user & AI messages in DB, and returns AI reply.
    """
    response = chat_with_llm(user_id, message)
    return {"reply": response}
