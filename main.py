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
app.include_router(chat_routes.router, prefix="/chats", tags=["Chat With Me"])
# Utility functions
def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

# ---------------- Register ----------------
@app.post("/register")
def register_user(
    name: str,
    email: str,
    password: str,
    craft: str = None,
    experience: str = None,
    location: str = None,
    db: Session = Depends(get_db),
):
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create user
    new_user = User(
        name=name,
        email=email,
        password=hash_password(password),
        craft=craft,
        experience=experience,
        location=location,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User registered successfully", "user_id": new_user.id}

# ---------------- Login ----------------
@app.post("/login")
def login_user(email: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {"message": "Login successful", "user_id": user.id}
