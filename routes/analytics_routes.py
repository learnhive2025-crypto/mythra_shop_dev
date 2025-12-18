from fastapi import APIRouter, Depends
from datetime import datetime, timedelta
from collections import defaultdict
from database import db
from utils.security import get_current_user
from bson import ObjectId

sales_collection = db["sales"]
products_collection = db["products"]

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)

# -------------------------------------------------
# 1️⃣ SLOW MOVING PRODUCTS
# -------------------------------------------------
@router.get("/slow-moving")
def slow_moving_products(
    days: int = 30,
    user=Depends(get_current_user)
):
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    sold_products = set()

    # products sold in last N days
    for sale in sales_collection.find(
        {"created_at": {"$gte": cutoff_date}},
        {"items.product_id": 1}
    ):
        for item in sale["items"]:
            sold_products.add(item["product_id"])

    result = []
    for product in products_collection.find({"is_active": True}):
        if str(product["_id"]) not in sold_products:
            result.append({
                "product_id": str(product["_id"]),
                "name": product["name"],
                "stock_qty": product["stock_qty"]
            })

    return result


# -------------------------------------------------
# 2️⃣ RESTOCK SUGGESTIONS (AI LOGIC)
# -------------------------------------------------
@router.get("/restock-suggestions")
def restock_suggestions(
    days: int = 30,
    min_days_left: int = 7,
    user=Depends(get_current_user)
):
    cutoff = datetime.utcnow() - timedelta(days=days)
    sales_map = defaultdict(int)

    # total sold per product
    for sale in sales_collection.find({"created_at": {"$gte": cutoff}}):
        for item in sale["items"]:
            sales_map[item["product_id"]] += item["qty"]

    result = []

    for product in products_collection.find({"is_active": True}):
        pid = str(product["_id"])
        sold_qty = sales_map.get(pid, 0)

        if sold_qty == 0:
            continue

        avg_daily_sales = sold_qty / days
        days_left = product["stock_qty"] / avg_daily_sales

        if days_left <= min_days_left:
            result.append({
                "product_id": pid,
                "name": product["name"],
                "stock_qty": product["stock_qty"],
                "avg_daily_sales": round(avg_daily_sales, 2),
                "days_of_stock_left": round(days_left, 1),
                "suggestion": "RESTOCK"
            })

    return result


# -------------------------------------------------
# 3️⃣ DEMAND PREDICTION
# -------------------------------------------------
@router.get("/demand-prediction")
def demand_prediction(
    past_days: int = 30,
    predict_days: int = 7,
    user=Depends(get_current_user)
):
    cutoff = datetime.utcnow() - timedelta(days=past_days)
    sales_map = defaultdict(int)

    for sale in sales_collection.find({"created_at": {"$gte": cutoff}}):
        for item in sale["items"]:
            sales_map[item["product_id"]] += item["qty"]

    result = []

    for product in products_collection.find({"is_active": True}):
        pid = str(product["_id"])
        sold_qty = sales_map.get(pid, 0)

        avg_daily = sold_qty / past_days if sold_qty > 0 else 0
        predicted = avg_daily * predict_days

        result.append({
            "product_id": pid,
            "name": product["name"],
            "avg_daily_sales": round(avg_daily, 2),
            "predicted_demand_next_days": round(predicted),
            "current_stock": product["stock_qty"]
        })

    return result
