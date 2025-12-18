from fastapi import APIRouter, Depends, HTTPException
from bson import ObjectId
from datetime import datetime

from database import users_collection
from schemas.user_schema import StaffCreateSchema, StaffUpdateSchema
from models.user_model import user_model
from utils.security import hash_password, admin_or_super_admin

router = APIRouter(
    prefix="/staff",
    tags=["Staff Management"]
)

# ------------------------------------
# CREATE STAFF
# ------------------------------------
@router.post("/create")
def create_staff(
    data: StaffCreateSchema,
    user=Depends(admin_or_super_admin)
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
            role="STAFF"
        )
    )

    return {"message": "Staff created successfully"}


# ------------------------------------
# LIST ALL STAFF
# ------------------------------------
@router.get("/list")
def list_staff(user=Depends(admin_or_super_admin)):
    staff_list = []

    for staff in users_collection.find(
        {"role": "STAFF", "is_active": True},
        {"password": 0}
    ):
        staff["_id"] = str(staff["_id"])
        staff_list.append(staff)

    return staff_list


# ------------------------------------
# GET SINGLE STAFF
# ------------------------------------
@router.get("/{staff_id}")
def get_staff(staff_id: str, user=Depends(admin_or_super_admin)):
    staff = users_collection.find_one(
        {"_id": ObjectId(staff_id), "role": "STAFF"},
        {"password": 0}
    )

    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found")

    staff["_id"] = str(staff["_id"])
    return staff


# ------------------------------------
# UPDATE STAFF
# ------------------------------------
@router.put("/update/{staff_id}")
def update_staff(
    staff_id: str,
    data: StaffUpdateSchema,
    user=Depends(admin_or_super_admin)
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
        {"_id": ObjectId(staff_id), "role": "STAFF"},
        {"$set": update_data}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Staff not found")

    return {"message": "Staff updated successfully"}


# ------------------------------------
# DELETE STAFF (SOFT DELETE)
# ------------------------------------
@router.delete("/delete/{staff_id}")
def delete_staff(staff_id: str, user=Depends(admin_or_super_admin)):
    result = users_collection.update_one(
        {"_id": ObjectId(staff_id), "role": "STAFF"},
        {
            "$set": {
                "is_active": False,
                "updated_at": datetime.utcnow()
            }
        }
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Staff not found")

    return {"message": "Staff deleted successfully"}
