from fastapi import FastAPI, HTTPException
from passlib.context import CryptContext
from routes import chat_routes
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from supabase_client import supabase
from routes import story_route
from routes import voice_story

app = FastAPI()


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.include_router(chat_routes.router, prefix="/chats", tags=["Chat With Me"])
app.include_router(story_route.router, prefix="/tools", tags=["Story Generator"])
app.include_router(voice_story.router, prefix="/voice", tags=["Story Generator"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "*",  # optional, for testing only
],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
):
    # Check if email already exists
    existing_user = supabase.table("users").select("*").eq("email", email).execute()
    if existing_user.data:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Insert new user
    hashed_pw = hash_password(password)
    response = supabase.table("users").insert({
        "name": name,
        "email": email,
        "password": hashed_pw,
        "craft": craft,
        "experience": experience,
        "location": location,
    }).execute()

    if not response.data:
        raise HTTPException(status_code=500, detail="Error creating user")

    return {"message": "User registered successfully", "user_id": response.data[0]["id"]}

# ---------------- Login ----------------
@app.post("/login")
def login_user(email: str, password: str):
    response = supabase.table("users").select("*").eq("email", email).execute()

    if not response.data:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    user = response.data[0]

    if not verify_password(password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {"message": "Login successful", "user_id": user["id"]}
