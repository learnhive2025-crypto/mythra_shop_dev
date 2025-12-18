from fastapi import APIRouter, Depends
from database import db
from utils.security import get_current_user
from collections import defaultdict

sales_collection = db["sales"]
products_collection = db["products"]

router = APIRouter(
    prefix="/profit",
    tags=["Profit"]
)

@router.get("/product-wise")
def product_wise_profit(user=Depends(get_current_user)):
    sold_qty_map = defaultdict(int)

    # collect sold quantity per product
    for sale in sales_collection.find():
        for item in sale["items"]:
            sold_qty_map[item["product_id"]] += item["qty"]

    result = []
    total_profit = 0

    for product_id, sold_qty in sold_qty_map.items():
        product = products_collection.find_one({"_id": product_id})
        if not product:
            continue

        profit = (product["selling_price"] - product["purchase_price"]) * sold_qty
        total_profit += profit

        result.append({
            "product_name": product["name"],
            "sold_qty": sold_qty,
            "profit": profit
        })

    return {
        "total_profit": total_profit,
        "product_wise_profit": result
    }
