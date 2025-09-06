from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session
from db import get_db
from models import ChatMessage
from workflow import social_media_workflow
from langchain_core.messages import HumanMessage, AIMessage
import os
import shutil
from uuid import uuid4

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def get_user_chat_history(user_id: int, db: Session):
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
    user_id: int = Form(...),
    query: str = Form(None),
    image: UploadFile = File(None),
    db: Session = Depends(get_db),
):
    image_url = None
    if image:
        # Give each file a unique name to prevent overwrites
        ext = image.filename.split(".")[-1]
        file_name = f"{uuid4()}.{ext}"
        image_path = os.path.join(UPLOAD_DIR, file_name)

        # Save file
        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        # Public URL (FastAPI serves this)
        image_url = f"/uploads/{file_name}"

    # Build content
    if query and image_url:
        content = f"[User Input] Text: {query} | Image: {image_url}"
    elif query:
        content = f"[User Input] Text: {query}"
    elif image_url:
        content = f"[User Input] Image: {image_url}"
    else:
        return {"error": "Either text or image required"}

    # Save user input
    user_msg = ChatMessage(user_id=user_id, role="human", message=content)
    db.add(user_msg)
    db.commit()
    db.refresh(user_msg)

    # Build history
    history = get_user_chat_history(user_id, db)
    history.append(HumanMessage(content=content))

    # Run workflow
    state = {"messages": history}
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
        "image_url": image_url,  # accessible public URL
    }
