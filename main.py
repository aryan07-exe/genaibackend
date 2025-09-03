from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from db import engine, Base, get_db
from models import User, ChatMessage
from passlib.context import CryptContext
from routes import chat_routes 

# Initialize FastAPI
app = FastAPI()

# Create tables
Base.metadata.create_all(bind=engine)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Utility functions
def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

app.include_router(chat_routes.router, prefix="/chat", tags=["Chat"])
# Register user
@app.post("/register")
def register_user(name: str, craft: str, location: str, experience: str, password: str, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.name == name).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    hashed_pw = hash_password(password)
    new_user = User(
        name=name,
        craft=craft,
        location=location,
        experience=experience,
        password=hashed_pw
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User registered successfully", "user_id": new_user.id}


# Login user
@app.post("/login")
def login_user(name: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.name == name).first()
    if not user or not verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"message": "Login successful", "user_id": user.id}


# Save chat message
@app.post("/chat")
def save_chat(user_id: int, role: str, message: str, db: Session = Depends(get_db)):
    if role not in ["human", "ai"]:
        raise HTTPException(status_code=400, detail="Role must be 'human' or 'ai'")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    chat_msg = ChatMessage(user_id=user_id, role=role, message=message)
    db.add(chat_msg)
    db.commit()
    db.refresh(chat_msg)
    return {"message": "Chat saved", "chat_id": chat_msg.id}


# Get chat history for a user
@app.get("/chat/{user_id}")
def get_chat_history(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    chats = db.query(ChatMessage).filter(ChatMessage.user_id == user_id).order_by(ChatMessage.timestamp).all()
    return [{"role": c.role, "message": c.message, "timestamp": c.timestamp} for c in chats]
