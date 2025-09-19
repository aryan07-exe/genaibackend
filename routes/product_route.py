from fastapi import APIRouter, UploadFile, Form
from services.product_tool import add_product, get_products, supabase
import uuid, os
import cloudinary
import cloudinary.uploader

router = APIRouter()

# Configure Cloudinary
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

# Upload image to Cloudinary
@router.post("/upload_image")
async def upload_image(file: UploadFile):
    upload_result = cloudinary.uploader.upload(file.file)
    image_url = upload_result["secure_url"]
    return {"image_url": image_url}

# Add product route
@router.post("/products")
async def create_product(
    artisan_id: str = Form(...),
    product_name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    image_url: str = Form(...)
):
    product_data = {
        "artisan_id": artisan_id,
        "product_name": product_name,
        "description": description,
        "price": price,
        "image_url": image_url
    }
    return {"status": "success", "data": add_product(product_data)}

# Fetch products route
@router.get("/products")
async def fetch_products():
    return {"products": get_products()}
