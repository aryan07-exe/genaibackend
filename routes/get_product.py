# routes/products.py
from fastapi import APIRouter, HTTPException
from supabase import create_client, Client
import os

router = APIRouter()



@router.get("/products")
async def get_products():
    try:
        response = supabase.table("products").select("*").execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="No products found")
        return {"products": response.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
