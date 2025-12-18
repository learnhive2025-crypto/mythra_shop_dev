from fastapi import APIRouter, Depends
from datetime import datetime, timedelta
from database import db
from utils.security import get_current_user

sales_collection = db["sales"]

router = APIRouter(
    prefix="/reports",
    tags=["Reports"]
)

# ---------------- DAILY SALES ----------------
@router.get("/daily-sales")
def daily_sales(user=Depends(get_current_user)):
    today = datetime.utcnow().date()
    total = 0

    for sale in sales_collection.find():
        if sale["created_at"].date() == today:
            total += sale["total_amount"]

    return {
        "date": str(today),
        "total_sales": total
    }

# ---------------- MONTHLY SALES ----------------
@router.get("/monthly-sales")
def monthly_sales(user=Depends(get_current_user)):
    now = datetime.utcnow()
    total = 0

    for sale in sales_collection.find():
        if sale["created_at"].year == now.year and sale["created_at"].month == now.month:
            total += sale["total_amount"]

    return {
        "month": f"{now.year}-{now.month}",
        "total_sales": total
    }
