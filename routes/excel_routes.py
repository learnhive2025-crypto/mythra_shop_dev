from fastapi import APIRouter
from fastapi.responses import FileResponse
from database import db
from bson import ObjectId
import pandas as pd

router = APIRouter(
    tags=["Excel"]
)

products_collection = db["products"]
categories_collection = db["categories"]

@router.get("/download-products")
def download_products_excel():
    data = []

    # Fetch all active products
    for p in products_collection.find({"is_active": True}):
        # Fetch category name
        category = categories_collection.find_one({"_id": ObjectId(p["category_id"])})
        
        data.append({
            "Product Name": p["name"],
            "Category": category["name"] if category else "N/A",
            "Barcode": p["barcode"],
            "Selling Price": p["selling_price"]
        })

    if not data:
        return {"message": "No products found to export"}

    df = pd.DataFrame(data)
    FILE_PATH = "product_barcodes.xlsx"
    df.to_excel(FILE_PATH, index=False)

    return FileResponse(
        path=FILE_PATH,
        filename="product_barcodes.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
