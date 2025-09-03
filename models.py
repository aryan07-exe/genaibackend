from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    craft = Column(String, nullable=False)   # artisan's craft / profession
    location = Column(String, nullable=False)
    experience = Column(String, nullable=False)
    password = Column(String, nullable=False)

    chats = relationship("ChatMessage", back_populates="user")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    role = Column(String, nullable=False)  # "human" or "ai"
    message = Column(String, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="chats")
