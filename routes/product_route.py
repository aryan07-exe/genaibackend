from fastapi import APIRouter, UploadFile, Form, File, HTTPException
from services.product_tool import add_product, get_products
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
    image: UploadFile = File(...)  # ✅ File instead of Form
):
    try:
        # 1️⃣ Upload image to Cloudinary
        upload_result = cloudinary.uploader.upload(image.file)
        image_url = upload_result.get("secure_url")

        if not image_url:
            raise HTTPException(status_code=500, detail="Image upload failed")

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
        raise HTTPException(status_code=500, detail=f"Error creating product: {str(e)}")


# Fetch products route (unchanged)
@router.get("/products")
async def fetch_products():
    return {"products": get_products()}

@router.delete("/products/{product_id}")
async def delete_product(product_id: str, artisan_id: str = Form(...)):
    try:
        # 1️⃣ Fetch product details
        product = get_product_by_id(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        # 2️⃣ Verify artisan ownership
        if product["artisan_id"] != artisan_id:
            raise HTTPException(status_code=403, detail="You are not allowed to delete this product")

        # 3️⃣ Delete product
        delete_success = delete_product_by_id(product_id)
        if not delete_success:
            raise HTTPException(status_code=500, detail="Failed to delete product")

        return {"status": "success", "message": f"Product {product_id} deleted successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting product: {str(e)}")