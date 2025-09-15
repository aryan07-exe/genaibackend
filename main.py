from fastapi import FastAPI, HTTPException
from passlib.context import CryptContext
from routes import chat_routes
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from supabase_client import supabase
from routes import story_route
from routes import voice_story
from routes import caption_route
from fastapi import FastAPI, Request
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

VERIFY_TOKEN = "secret_token"  # ye wahi token hai jo FB me dala hai



CLIENT_ID = os.getenv("ig_id")  # Instagram App ID
CLIENT_SECRET = os.getenv("ig_secret")  # Instagram App Secret
REDIRECT_URI = "https://genaibackend-r809.onrender.com"

@app.get("/instagram/callback")
async def instagram_callback(request: Request):
    code = request.query_params.get('code')
    
    if not code:
        return {"error": "Missing code in query parameters."}

    # Exchange code for access token
    token_url = "https://graph.facebook.com/v15.0/oauth/access_token"
    params = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI,
        "code": code
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(token_url, params=params)
        data = response.json()

    if "access_token" not in data:
        return {"error": "Failed to get access token", "details": data}

    access_token = data["access_token"]

    # TODO: Save access_token securely in your database for the logged-in user

    # Example: Redirect to a frontend page after successful login
    return RedirectResponse(url=f"https://yourfrontend.com/login-success?access_token={access_token}")



@app.get("/webhook")
async def verify_webhook(request: Request):
    """
    Facebook webhook verification
    FB verify request bhejta hai GET me
    """
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")
    
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return int(challenge)  # FB expects the challenge number back
    else:
        raise HTTPException(status_code=403, detail="Verification failed")

@app.post("/webhook")
async def receive_webhook(request: Request):
    """
    Actual webhook event receive karne ke liye POST endpoint
    """
    data = await request.json()
    print("Webhook data received:", data)
    return {"status": "received"}

@app.get("/auth/facebook/callback")
async def facebook_callback(request: Request):
    code = request.query_params.get("code")
    if not code:
        return {"error": "Missing code parameter"}

    # Exchange code for access token
    access_token_url = "https://graph.facebook.com/v15.0/oauth/access_token"
    params = {
        "client_id": "YOUR_FACEBOOK_CLIENT_ID",
        "client_secret": "YOUR_FACEBOOK_CLIENT_SECRET",
        "redirect_uri": "https://yourdomain.com/auth/facebook/callback",
        "code": code
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(access_token_url, params=params)
        token_data = response.json()

    return {"message": "Facebook login successful", "token_data": token_data}

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.include_router(chat_routes.router, prefix="/chats", tags=["Chat With Me"])
app.include_router(story_route.router, prefix="/tools", tags=["Story Generator"])
app.include_router(voice_story.router, prefix="/voice", tags=["Story voice Generator"])
app.include_router(caption_route.router, prefix="/caption", tags=["Caption Generator"])
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
