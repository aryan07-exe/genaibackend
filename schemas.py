from pydantic import BaseModel, EmailStr
from typing import List, Optional
import uuid

# User Schemas
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    craft: Optional[str] = None
    experience: Optional[str] = None
    location: Optional[str] = None

class UserResponse(BaseModel):
    id: uuid.UUID
    name: str
    email: EmailStr
    craft: Optional[str] = None
    experience: Optional[str] = None
    location: Optional[str] = None

    class Config:
        orm_mode = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Chat Schemas
class ChatCreate(BaseModel):
    user_id: uuid.UUID
    role: str  # 'user' or 'assistant'
    message: str

class ChatResponse(BaseModel):
    id: int
    user_id: uuid.UUID
    role: str
    message: str

    class Config:
        orm_mode = True

class ChatHistoryResponse(BaseModel):
    chats: List[ChatResponse]
