from sqlalchemy import Column, String, Text, ForeignKey, TIMESTAMP, func, BigInteger
from sqlalchemy.dialects.postgresql import UUID
import uuid
from db import Base  # Assuming you have db.py with SQLAlchemy Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    craft = Column(Text, nullable=True)
    experience = Column(Text, nullable=True)
    location = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())


class ChatMessage(Base):
    __tablename__ = "chat"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    role = Column(String, nullable=False)  # 'user' or 'assistant'
    message = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
