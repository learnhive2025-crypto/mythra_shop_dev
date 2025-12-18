from fastapi import APIRouter, Depends
from database import db
from utils.security import get_current_user

products_collection = db["products"]

router = APIRouter(
    prefix="/stock",
    tags=["Stock"]
)

# ---------------- STOCK SUMMARY ----------------
@router.get("/summary")
def stock_summary(user=Depends(get_current_user)):
    result = []

    for p in products_collection.find({"is_active": True}):
        result.append({
            "product_id": str(p["_id"]),
            "name": p["name"],
            "stock_qty": p["stock_qty"]
        })

    return result


# ---------------- LOW STOCK ALERT ----------------
@router.get("/low-stock")
def low_stock_alert(
    threshold: int = 10,
    user=Depends(get_current_user)
):
    result = []

    for p in products_collection.find({
        "is_active": True,
        "stock_qty": {"$lte": threshold}
    }):
        result.append({
            "product_id": str(p["_id"]),
            "name": p["name"],
            "stock_qty": p["stock_qty"]
        })

    return result
