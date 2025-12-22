from fastapi import APIRouter, Depends
from collections import defaultdict
from datetime import datetime, timedelta
from bson import ObjectId
from database import db
from utils.security import get_current_user

users_collection = db["users"]
categories_collection = db["categories"]
products_collection = db["products"]
sales_collection = db["sales"]
purchases_collection = db["purchases"]
expenses_collection = db["expenses"]

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)

# ---------------- DASHBOARD SUMMARY ----------------
@router.get("/summary")
def dashboard_summary(user=Depends(get_current_user)):
    total_admins = users_collection.count_documents(
        {"role": {"$in": ["admin", "super_admin"]}}
    )
    total_staff = users_collection.count_documents({"role": "staff"})

    total_categories = categories_collection.count_documents({"is_active": True})
    total_products = products_collection.count_documents({"is_active": True})

    purchase_qty = sum(p.get("qty", 0) for p in purchases_collection.find())

    total_sales = sales_collection.count_documents({})
    total_revenue = sum(s.get("total_amount", 0) for s in sales_collection.find())

    # Calculate total expenses
    pipeline = [
        {"$match": {"is_active": True}},
        {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
    ]
    expense_result = list(expenses_collection.aggregate(pipeline))
    total_expenses = expense_result[0]["total"] if expense_result else 0

    return {
        "admins": total_admins,
        "staff": total_staff,
        "categories": total_categories,
        "products": total_products,
        "purchase_qty": purchase_qty,
        "total_sales": total_sales,
        "total_revenue": total_revenue,
        "total_expenses": total_expenses
    }


# ---------------- SALES ANALYSIS ----------------
@router.get("/sales-analysis")
def sales_analysis(user=Depends(get_current_user)):
    now = datetime.utcnow()
    today_start = datetime(now.year, now.month, now.day)
    week_start = today_start - timedelta(days=now.weekday())
    month_start = datetime(now.year, now.month, 1)

    daily = weekly = monthly = 0

    for sale in sales_collection.find():
        created = sale["created_at"]
        amount = sale.get("total_amount", 0)

        if created >= today_start:
            daily += amount
        if created >= week_start:
            weekly += amount
        if created >= month_start:
            monthly += amount

    return {
        "daily_sales": daily,
        "weekly_sales": weekly,
        "monthly_sales": monthly
    }


# ---------------- TOP SELLING PRODUCTS ----------------
@router.get("/top-products")
def top_selling_products(user=Depends(get_current_user)):
    sales_map = defaultdict(int)

    for sale in sales_collection.find():
        for item in sale["items"]:
            sales_map[item["product_id"]] += item["qty"]

    result = []
    for product_id, qty in sales_map.items():
        product = products_collection.find_one({"_id": ObjectId(product_id)})
        if product:
            result.append({
                "product_id": product_id,
                "name": product["name"],
                "sold_qty": qty
            })

    result.sort(key=lambda x: x["sold_qty"], reverse=True)
    return result
