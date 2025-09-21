from fastapi import APIRouter, UploadFile, Form, HTTPException
from services.product_tool import add_product, get_products, supabase
import os
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv

load_dotenv()
router = APIRouter()

# Configure Cloudinary
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

# Create product with image in one step
@router.post("/products")
async def create_product_with_image(
    artisan_id: str = Form(...),
    product_name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    image: UploadFile = Form(...)
):
    try:
        # 1️⃣ Upload image to Cloudinary
        upload_result = cloudinary.uploader.upload(image.file)
        image_url = upload_result["secure_url"]

        # 2️⃣ Prepare product data
        product_data = {
            "artisan_id": artisan_id,
            "product_name": product_name,
            "description": description,
            "price": price,
            "image_url": image_url
        }

        # 3️⃣ Insert product into database
        added_product = add_product(product_data)

        return {"status": "success", "data": added_product}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Fetch products route (unchanged)
@router.get("/products")
async def fetch_products():
    return {"products": get_products()}
