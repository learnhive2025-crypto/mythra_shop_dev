from fastapi import APIRouter, Depends, HTTPException
from bson import ObjectId
from datetime import datetime
from utils.barcode_utils import generate_barcode
from database import db
from models.product_model import product_model
from schemas.product_schema import ProductCreateSchema, ProductUpdateSchema
from utils.security import get_current_user, admin_or_super_admin
from utils.excel_utils import append_product_to_excel
products_collection = db["products"]
categories_collection = db["categories"]

router = APIRouter(
    prefix="/products",
    tags=["Products"]
)

# -------------------------------------------------
# ADD PRODUCT
# Access: Super Admin, Admin, Staff
# -------------------------------------------------
@router.post("/add")
def add_product(
    data: ProductCreateSchema,
    user=Depends(get_current_user)
):
    category = categories_collection.find_one({
        "_id": ObjectId(data.category_id),
        "is_active": True
    })

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    barcode = generate_barcode()

    products_collection.insert_one(
        product_model(
            name=data.name,
            category_id=data.category_id,
            purchase_price=data.purchase_price,
            selling_price=data.selling_price,
            barcode=barcode,
            stock_qty=data.stock_qty
        )
    )

    # ✅ APPEND TO EXCEL
    append_product_to_excel({
        "name": data.name,
        "category": category["name"],
        "barcode": barcode,
        "selling_price": data.selling_price
    })

    return {
        "message": "Product added successfully",
        "barcode": barcode
    }
# -------------------------------------------------
# LIST PRODUCTS
# Access: Super Admin, Admin, Staff
# -------------------------------------------------
@router.get("/list")
def list_products(user=Depends(get_current_user)):
    result = []

    for product in products_collection.find({"is_active": True}):
        category = categories_collection.find_one(
            {"_id": ObjectId(product["category_id"])},
            {"name": 1}
        )

        result.append({
            "id": str(product["_id"]),
            "name": product["name"],
            "category": category["name"] if category else None,
            "purchase_price": product["purchase_price"],
            "selling_price": product["selling_price"],
            "stock_qty": product["stock_qty"]
        })

    return result

# -------------------------------------------------
# UPDATE PRODUCT
# Access: Super Admin, Admin ONLY
# -------------------------------------------------
@router.put("/update/{product_id}")
def update_product(
    product_id: str,
    data: ProductUpdateSchema,
    user=Depends(admin_or_super_admin)
):
    update = products_collection.update_one(
        {"_id": ObjectId(product_id)},
        {
            "$set": {
                "name": data.name,
                "category_id": data.category_id,
                "purchase_price": data.purchase_price,
                "selling_price": data.selling_price,
                "stock_qty": data.stock_qty,
                "is_active": data.is_active,
                "updated_at": datetime.utcnow()
            }
        }
    )

    if update.matched_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")

    return {"message": "Product updated successfully"}

# -------------------------------------------------
# DELETE PRODUCT (SOFT DELETE)
# Access: Super Admin, Admin ONLY
# -------------------------------------------------
@router.delete("/delete/{product_id}")
def delete_product(
    product_id: str,
    user=Depends(admin_or_super_admin)
):
    delete = products_collection.update_one(
        {"_id": ObjectId(product_id)},
        {
            "$set": {
                "is_active": False,
                "updated_at": datetime.utcnow()
            }
        }
    )

    if delete.matched_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")

    return {"message": "Product deleted successfully"}

@router.get("/by-barcode/{barcode}")
def get_product_by_barcode(barcode: str, user=Depends(get_current_user)):
    product = products_collection.find_one({
        "barcode": barcode,
        "is_active": True
    })

    if not product:
        raise HTTPException(404, "Product not found")

    return {
        "id": str(product["_id"]),
        "name": product["name"],
        "selling_price": product["selling_price"]
    }
