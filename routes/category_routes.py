from fastapi import APIRouter, Depends, HTTPException
from bson import ObjectId
from datetime import datetime

from database import db
from models.category_model import category_model
from schemas.category_schema import CategoryCreateSchema, CategoryUpdateSchema
from utils.security import (
    get_current_user,
    admin_or_super_admin
)

categories_collection = db["categories"]

router = APIRouter(
    prefix="/categories",
    tags=["Categories"]
)

# ---------------- ADD CATEGORY ----------------
# Super Admin, Admin, Staff
@router.post("/add")
def add_category(
    data: CategoryCreateSchema,
    user=Depends(get_current_user)
):
    if categories_collection.find_one({"name": data.name}):
        raise HTTPException(status_code=400, detail="Category already exists")

    categories_collection.insert_one(
        category_model(name=data.name)
    )
    return {"message": "Category added successfully"}

# ---------------- LIST CATEGORIES ----------------
# Super Admin, Admin, Staff
@router.get("/list")
def list_categories(user=Depends(get_current_user)):
    categories = []
    for cat in categories_collection.find({"is_active": True}):
        categories.append({
            "id": str(cat["_id"]),
            "name": cat["name"]
        })
    return categories

# ---------------- UPDATE CATEGORY ----------------
# Super Admin, Admin only
@router.put("/update/{category_id}")
def update_category(
    category_id: str,
    data: CategoryUpdateSchema,
    user=Depends(admin_or_super_admin)
):
    result = categories_collection.update_one(
        {"_id": ObjectId(category_id)},
        {
            "$set": {
                "name": data.name,
                "is_active": data.is_active,
                "updated_at": datetime.utcnow()
            }
        }
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Category not found")

    return {"message": "Category updated successfully"}

# ---------------- DELETE CATEGORY ----------------
# Super Admin, Admin only (soft delete)
@router.delete("/delete/{category_id}")
def delete_category(
    category_id: str,
    user=Depends(admin_or_super_admin)
):
    result = categories_collection.update_one(
        {"_id": ObjectId(category_id)},
        {
            "$set": {
                "is_active": False,
                "updated_at": datetime.utcnow()
            }
        }
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Category not found")

    return {"message": "Category deleted successfully"}
