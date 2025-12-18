from fastapi import APIRouter, HTTPException
from database import users_collection
from schemas.user_schema import LoginSchema
from utils.security import verify_password, create_token
from datetime import datetime   # ✅ add this

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login")
def login(data: LoginSchema):
    user = users_collection.find_one({"username": data.username})

    if not user or not verify_password(data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not user["is_active"]:
        raise HTTPException(status_code=403, detail="User inactive")

    # ✅ UPDATE last_login + updated_at
    users_collection.update_one(
        {"_id": user["_id"]},
        {
            "$set": {
                "last_login": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        }
    )

    token = create_token({
        "user_id": str(user["_id"]),
        "role": user["role"]
    })

    return {
        "access_token": token,
        "role": user["role"],
        "username": user["username"],
        "email": user["email"]
    }
