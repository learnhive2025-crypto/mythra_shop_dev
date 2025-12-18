from fastapi import APIRouter, Depends, HTTPException
from database import db
from models.sales_model import sales_model
from schemas.sales_schema import SalesCreateSchema
from utils.security import get_current_user
from bson import ObjectId
products_collection = db["products"]
sales_collection = db["sales"]

router = APIRouter(
    prefix="/sales",
    tags=["Sales"]
)

# ---------------- ADD SALE (STOCK OUT - BARCODE) ----------------
@router.post("/add")
def add_sale(
    data: SalesCreateSchema,
    user=Depends(get_current_user)   # Staff / Admin / Super Admin
):
    total_amount = 0
    sales_items = []

    for item in data.items:
        # 🔍 FIND PRODUCT BY BARCODE
        product = products_collection.find_one({
            "barcode": item.barcode,
            "is_active": True
        })

        if not product:
            raise HTTPException(
                status_code=404,
                detail=f"Product not found for barcode {item.barcode}"
            )

        # ❌ PREVENT NEGATIVE STOCK
        if product["stock_qty"] < item.qty:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock for {product['name']}"
            )

        # 🔽 STOCK OUT
        products_collection.update_one(
            {"_id": product["_id"]},
            {"$inc": {"stock_qty": -item.qty}}
        )

        amount = product["selling_price"] * item.qty
        total_amount += amount

        sales_items.append({
            "product_id": str(product["_id"]),
            "barcode": item.barcode,
            "qty": item.qty,
            "price": product["selling_price"]
        })

    sales_collection.insert_one(
        sales_model(
            bill_no=data.bill_no,
            items=sales_items,
            total_amount=total_amount,
            payment_mode=data.payment_mode,
            created_by=user["user_id"]
        )
    )

    return {
        "message": "Sale completed successfully",
        "total_amount": total_amount
    }
# ---------------- LIST SALES ----------------
@router.get("/list")
def list_sales(user=Depends(get_current_user)):
    result = []

    for sale in sales_collection.find().sort("created_at", -1):
        result.append({
            "id": str(sale["_id"]),
            "bill_no": sale["bill_no"],
            "items": sale["items"],
            "total_amount": sale["total_amount"],
            "payment_mode": sale["payment_mode"],
            "created_at": sale["created_at"]
        })

    return result
# ---------------- SALE DETAILS ----------------
@router.get("/details/{sale_id}")
def sale_details(
    sale_id: str,
    user=Depends(get_current_user)
):
    sale = sales_collection.find_one({"_id": ObjectId(sale_id)})

    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")

    return {
        "id": str(sale["_id"]),
        "bill_no": sale["bill_no"],
        "items": sale["items"],
        "total_amount": sale["total_amount"],
        "payment_mode": sale["payment_mode"],
        "created_at": sale["created_at"]
    }
