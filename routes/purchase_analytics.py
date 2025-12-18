from fastapi import APIRouter, Depends
from datetime import datetime, timedelta
from collections import defaultdict
from bson import ObjectId

from database import db
from utils.security import admin_or_super_admin

purchases_collection = db["purchases"]
products_collection = db["products"]

router = APIRouter(
    prefix="/purchase-analytics",
    tags=["Purchase Analytics"]
)

# -------------------------------------------------
# 3️⃣ SUPPLIER ANALYTICS
# -------------------------------------------------
@router.get("/supplier-wise")
def supplier_analytics(user=Depends(admin_or_super_admin)):
    supplier_map = defaultdict(lambda: {
        "total_amount": 0,
        "purchase_count": 0
    })

    for p in purchases_collection.find({"is_active": True}):
        supplier = p["supplier_name"]
        supplier_map[supplier]["total_amount"] += p["total_amount"]
        supplier_map[supplier]["purchase_count"] += 1

    result = []
    for supplier, data in supplier_map.items():
        result.append({
            "supplier_name": supplier,
            "total_purchase_amount": data["total_amount"],
            "purchase_count": data["purchase_count"]
        })

    result.sort(
        key=lambda x: x["total_purchase_amount"],
        reverse=True
    )

    return result


# -------------------------------------------------
# 4️⃣ PURCHASE CHART (DAILY / MONTHLY)
# -------------------------------------------------
@router.get("/purchase-chart")
def purchase_chart(
    period: str = "daily",  # daily | monthly
    user=Depends(admin_or_super_admin)
):
    chart_map = defaultdict(int)

    for p in purchases_collection.find({"is_active": True}):
        date = p["created_at"]

        if period == "monthly":
            key = date.strftime("%Y-%m")
        else:
            key = date.strftime("%Y-%m-%d")

        chart_map[key] += p["total_amount"]

    return [
        {"label": k, "value": v}
        for k, v in sorted(chart_map.items())
    ]


# -------------------------------------------------
# 5️⃣ AI PURCHASE SUGGESTIONS 🤖
# -------------------------------------------------
@router.get("/ai-purchase-suggestions")
def ai_purchase_suggestions(
    days: int = 30,
    predict_days: int = 7,
    user=Depends(admin_or_super_admin)
):
    cutoff = datetime.utcnow() - timedelta(days=days)
    purchase_map = defaultdict(int)

    for p in purchases_collection.find(
        {"created_at": {"$gte": cutoff}, "is_active": True}
    ):
        for item in p["items"]:
            purchase_map[item["product_id"]] += item["qty"]

    result = []

    for product in products_collection.find({"is_active": True}):
        pid = str(product["_id"])
        purchased_qty = purchase_map.get(pid, 0)

        if purchased_qty == 0:
            continue

        avg_daily_purchase = purchased_qty / days
        predicted_need = avg_daily_purchase * predict_days

        if product["stock_qty"] < predicted_need:
            result.append({
                "product_id": pid,
                "product_name": product["name"],
                "current_stock": product["stock_qty"],
                "avg_daily_purchase": round(avg_daily_purchase, 2),
                "predicted_required_qty": round(predicted_need),
                "suggestion": "PURCHASE"
            })

    return result
