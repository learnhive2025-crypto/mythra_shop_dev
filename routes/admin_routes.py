from fastapi import APIRouter, Depends, HTTPException
from bson import ObjectId
from datetime import datetime

from database import users_collection
from schemas.user_schema import AdminCreateSchema, AdminUpdateSchema
from models.user_model import user_model
from utils.security import hash_password, super_admin_only

router = APIRouter(
    prefix="/admin",
    tags=["Admin Management"]
)

# ------------------------------------
# CREATE ADMIN (SUPER ADMIN ONLY)
# ------------------------------------
@router.post("/create")
def create_admin(
    data: AdminCreateSchema,
    user=Depends(super_admin_only)
):
    if users_collection.find_one({
        "$or": [
            {"username": data.username},
            {"email": data.email}
        ]
    }):
        raise HTTPException(status_code=400, detail="User already exists")

    users_collection.insert_one(
        user_model(
            username=data.username,
            email=data.email,
            password=hash_password(data.password),
            role="ADMIN"
        )
    )

    return {"message": "Admin created successfully"}


# ------------------------------------
# LIST ALL ADMINS
# ------------------------------------
@router.get("/list")
def list_admins(user=Depends(super_admin_only)):
    admins = []

    for admin in users_collection.find(
        {"role": "ADMIN", "is_active": True},
        {"password": 0}
    ):
        admin["_id"] = str(admin["_id"])
        admins.append(admin)

    return admins


# ------------------------------------
# GET SINGLE ADMIN
# ------------------------------------
@router.get("/{admin_id}")
def get_admin(admin_id: str, user=Depends(super_admin_only)):
    admin = users_collection.find_one(
        {"_id": ObjectId(admin_id), "role": "ADMIN"},
        {"password": 0}
    )

    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")

    admin["_id"] = str(admin["_id"])
    return admin


# ------------------------------------
# UPDATE ADMIN
# ------------------------------------
@router.put("/update/{admin_id}")
def update_admin(
    admin_id: str,
    data: AdminUpdateSchema,
    user=Depends(super_admin_only)
):
    update_data = {}

    if data.username:
        update_data["username"] = data.username
    if data.email:
        update_data["email"] = data.email
    if data.password:
        update_data["password"] = hash_password(data.password)

    if not update_data:
        raise HTTPException(status_code=400, detail="No data to update")

    update_data["updated_at"] = datetime.utcnow()

    result = users_collection.update_one(
        {"_id": ObjectId(admin_id), "role": "ADMIN"},
        {"$set": update_data}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Admin not found")

    return {"message": "Admin updated successfully"}


# ------------------------------------
# DELETE ADMIN (SOFT DELETE)
# ------------------------------------
@router.delete("/delete/{admin_id}")
def delete_admin(admin_id: str, user=Depends(super_admin_only)):
    result = users_collection.update_one(
        {"_id": ObjectId(admin_id), "role": "ADMIN"},
        {
            "$set": {
                "is_active": False,
                "updated_at": datetime.utcnow()
            }
        }
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Admin not found")

    return {"message": "Admin deleted successfully"}
