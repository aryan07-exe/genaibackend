from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session
from db import get_db
from models import ChatMessage
from workflow import social_media_workflow
from langchain_core.messages import HumanMessage, AIMessage
import os
import shutil
from uuid import UUID
import base64
from typing import Optional, Union
router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def get_user_chat_history(user_id: UUID, db: Session):
    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.user_id == user_id)
        .order_by(ChatMessage.timestamp.asc())
        .all()
    )

    history = []
    for msg in messages:
        if msg.role == "human":
            history.append(HumanMessage(content=msg.message))
        else:
            history.append(AIMessage(content=msg.message))
    return history

@router.post("/assistant/social")
async def social_media_chat(
    user_id: UUID = Form(...),
    query: str = Form(None),                  # optional text
    image: UploadFile = File(None),           # optional image
    db: Session = Depends(get_db),
):
    image_base64 = None

    # If an image is uploaded, save it and convert to base64
    if image:
        if not os.path.exists(UPLOAD_DIR):
            os.makedirs(UPLOAD_DIR)
        image_path = os.path.join(UPLOAD_DIR, image.filename)
        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        
        # Convert image to base64 so AI can process it
        image_bytes = open(image_path, "rb").read()
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")

    # Build content for AI
    if query and image_base64:
        content = f"[User Input] Text: {query} | Image included (base64)"
    elif query:
        content = f"[User Input] Text: {query}"
    elif image_base64:
        content = "[User Input] Image included (base64)"
    else:
        content = "[User Input] Empty message"

    # Save user message in DB
    user_msg = ChatMessage(user_id=user_id, role="human", message=content)
    db.add(user_msg)
    db.commit()
    db.refresh(user_msg)

    # Build chat history
    history = get_user_chat_history(user_id, db)
    history.append(HumanMessage(content=content))

    # Run AI workflow, include image_base64 in state if exists
    state = {"messages": history}
    if image_base64:
        state["image_base64"] = image_base64

    result = social_media_workflow.invoke(state)
    ai_msg_obj = result["messages"][-1]
    response = ai_msg_obj.content

    # Save AI response
    ai_msg = ChatMessage(user_id=user_id, role="ai", message=response)
    db.add(ai_msg)
    db.commit()
    db.refresh(ai_msg)

    return {
        "response": response,
        "user_message_id": user_msg.id,
        "ai_message_id": ai_msg.id,
        "image_uploaded": bool(image_base64),
    }