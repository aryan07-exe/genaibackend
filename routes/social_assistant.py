from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db import get_db
from models import ChatMessage
from workflow import social_media_workflow

router = APIRouter()

from langchain_core.messages import HumanMessage, AIMessage

def get_user_chat_history(user_id: int, db: Session):
    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.user_id == user_id)
        .order_by(ChatMessage.timestamp.asc())
        .all()
    )

    # Convert DB rows into LangChain messages
    history = []
    for msg in messages:
        if msg.role == "human":
            history.append(HumanMessage(content=msg.message))
        else:
            history.append(AIMessage(content=msg.message))
    return history
@router.post("/assistant/social")
def social_media_chat(query: str, user_id: int, db: Session = Depends(get_db)):
    from langchain_core.messages import HumanMessage

    # Save user message in DB
    user_msg = ChatMessage(user_id=user_id, role="human", message=query)
    db.add(user_msg)
    db.commit()
    db.refresh(user_msg)

    # Get previous history
    history = get_user_chat_history(user_id, db)

    # Add new query as last message
    history.append(HumanMessage(content=query))

    # Run workflow with full history
    state = {"messages": history}
    result = social_media_workflow.invoke(state)

    ai_msg_obj = result["messages"][-1]
    response = ai_msg_obj.content

    # Save AI message in DB
    ai_msg = ChatMessage(user_id=user_id, role="ai", message=response)
    db.add(ai_msg)
    db.commit()
    db.refresh(ai_msg)

    return {
        "response": response,
        "user_message_id": user_msg.id,
        "ai_message_id": ai_msg.id
    }
