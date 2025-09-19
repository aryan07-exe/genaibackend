from supabase import create_client, Client
import os

# Setup Supabase client
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def add_product(product_data: dict):
    """
    Insert a product into Supabase products table.
    product_data should contain:
    {
        "artisan_id": "uuid",
        "product_name": "string",
        "description": "string",
        "price": float,
        "image_url": "string"
    }
    """
    response = supabase.table("products").insert(product_data).execute()
    return response.data

def get_products():
    """
    Fetch all products from Supabase.
    """
    response = supabase.table("products").select("*").execute()
    return response.data
