from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from db import engine, Base, get_db
from models import User, ChatMessage
from passlib.context import CryptContext
from routes import chat_routes 
from fastapi.middleware.cors import CORSMiddleware
from routes import social_assistant
from fastapi.staticfiles import StaticFiles

# Initialize FastAPI
app = FastAPI()

# Create tables
Base.metadata.create_all(bind=engine)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.include_router(social_assistant.router)
# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:3000"] for more security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Utility functions
def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

app.include_router(chat_routes.router, prefix="/chats", tags=["Chat With Me"])
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
 
