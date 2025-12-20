from fastapi import APIRouter, Depends, HTTPException
from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime

from database import db
from schemas.purchase_schema import (
    PurchaseCreateSchema,
    PurchaseUpdateSchema
)
from utils.security import admin_or_super_admin

# Collections
products_collection = db["products"]
purchases_collection = db["purchases"]

router = APIRouter(
    prefix="/purchases",
    tags=["Purchases"]
)

# -------------------------------------------------
# PURCHASE MODEL
# -------------------------------------------------
def purchase_model(invoice_no, supplier_name, items, total_amount):
    return {
        "invoice_no": invoice_no,
        "supplier_name": supplier_name,
        "items": items,
        "total_amount": total_amount,
        "is_active": True,
        "created_at": datetime.utcnow(),
        "updated_at": None
    }

# -------------------------------------------------
# ADD PURCHASE (STOCK IN)
# -------------------------------------------------
@router.post("/add")
def add_purchase(
    data: PurchaseCreateSchema,
    user=Depends(admin_or_super_admin)
):
    try:
        total_amount = 0

        for item in data.items:
            try:
                product_oid = ObjectId(item.product_id)
            except InvalidId:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid product id: {item.product_id}"
                )

            product = products_collection.find_one({
                "_id": product_oid,
                "is_active": True
            })

            if not product:
                raise HTTPException(
                    status_code=404,
                    detail="Product not found"
                )

            products_collection.update_one(
                {"_id": product_oid},
                {"$inc": {"stock_qty": item.qty}}
            )

            total_amount += item.qty * item.price

        purchases_collection.insert_one(
            purchase_model(
                invoice_no=data.invoice_no,
                supplier_name=data.supplier_name,
                items=[item.dict() for item in data.items],
                total_amount=total_amount
            )
        )

        return {
            "message": "Purchase added successfully",
            "total_amount": total_amount
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Purchase failed: {str(e)}"
        )

# -------------------------------------------------
# LIST PURCHASES
# -------------------------------------------------
@router.get("/list")
def list_purchases(user=Depends(admin_or_super_admin)):
    return [
        {
            "_id": str(p["_id"]),
            "invoice_no": p["invoice_no"],
            "supplier_name": p["supplier_name"],
            "total_amount": p["total_amount"],
            "created_at": p["created_at"]
        }
        for p in purchases_collection.find({"is_active": True})
    ]

# -------------------------------------------------
# GET PURCHASE
# -------------------------------------------------
@router.get("/{purchase_id}")
def get_purchase(purchase_id: str, user=Depends(admin_or_super_admin)):
    try:
        purchase_oid = ObjectId(purchase_id)
    except InvalidId:
        raise HTTPException(400, "Invalid purchase id")

    purchase = purchases_collection.find_one({
        "_id": purchase_oid,
        "is_active": True
    })

    if not purchase:
        raise HTTPException(404, "Purchase not found")

    purchase["_id"] = str(purchase["_id"])
    return purchase

# -------------------------------------------------
# UPDATE PURCHASE
# -------------------------------------------------
@router.put("/update/{purchase_id}")
def update_purchase(
    purchase_id: str,
    data: PurchaseUpdateSchema,
    user=Depends(admin_or_super_admin)
):
    try:
        purchase_oid = ObjectId(purchase_id)
    except InvalidId:
        raise HTTPException(400, "Invalid purchase id")

    old_purchase = purchases_collection.find_one({
        "_id": purchase_oid,
        "is_active": True
    })

    if not old_purchase:
        raise HTTPException(404, "Purchase not found")

    # 🔁 REVERSE OLD STOCK
    for item in old_purchase["items"]:
        products_collection.update_one(
            {"_id": ObjectId(item["product_id"])},
            {"$inc": {"stock_qty": -item["qty"]}}
        )

    total_amount = 0

    # 🔥 APPLY NEW STOCK
    for item in data.items:
        try:
            product_oid = ObjectId(item.product_id)
        except InvalidId:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid product id: {item.product_id}"
            )

        product = products_collection.find_one({
            "_id": product_oid,
            "is_active": True
        })

        if not product:
            raise HTTPException(
                status_code=404,
                detail="Product not found"
            )

        products_collection.update_one(
            {"_id": product_oid},
            {"$inc": {"stock_qty": item.qty}}
        )

        total_amount += item.qty * item.price

    purchases_collection.update_one(
        {"_id": purchase_oid},
        {
            "$set": {
                "invoice_no": data.invoice_no,
                "supplier_name": data.supplier_name,
                "items": [item.dict() for item in data.items],
                "total_amount": total_amount,
                "updated_at": datetime.utcnow()
            }
        }
    )

    return {"message": "Purchase updated successfully"}

# -------------------------------------------------
# DELETE PURCHASE
# -------------------------------------------------
@router.delete("/delete/{purchase_id}")
def delete_purchase(
    purchase_id: str,
    user=Depends(admin_or_super_admin)
):
    try:
        purchase_oid = ObjectId(purchase_id)
    except InvalidId:
        raise HTTPException(400, "Invalid purchase id")

    purchase = purchases_collection.find_one({
        "_id": purchase_oid,
        "is_active": True
    })

    if not purchase:
        raise HTTPException(404, "Purchase not found")

    # 🔁 REVERSE STOCK
    for item in purchase["items"]:
        products_collection.update_one(
            {"_id": ObjectId(item["product_id"])},
            {"$inc": {"stock_qty": -item["qty"]}}
        )

    purchases_collection.update_one(
        {"_id": purchase_oid},
        {
            "$set": {
                "is_active": False,
                "updated_at": datetime.utcnow()
            }
        }
    )

    return {"message": "Purchase deleted successfully"}
