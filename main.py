from fastapi import FastAPI
from database import users_collection
from models.user_model import user_model
from utils.security import hash_password
from config import (
    SUPER_ADMIN_USERNAME,
    SUPER_ADMIN_EMAIL,
    SUPER_ADMIN_PASSWORD
)
from fastapi.middleware.cors import CORSMiddleware
from api import api_router  

app = FastAPI(title="Retail Stock Management Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://pos-management-rosy.vercel.app",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# -------- SUPER ADMIN AUTO CREATE --------
# ✅ Moved to startup event to prevent import crash
@app.on_event("startup")
async def startup_event():
    try:
        print("🔄 Checking database connection...")
        # Simple check to trigger connection
        users_collection.database.command("ping")
        print("✅ Database Connected")
        
        create_default_super_admin()
    except Exception as e:
        print(f"⚠️ Database Connection Warning: {e}")
        print("⚠️ Ensure your IP is whitelisted in MongoDB Atlas.")

from fastapi import Request
from fastapi.responses import JSONResponse
from pymongo.errors import PyMongoError

@app.exception_handler(PyMongoError)
async def pymongo_exception_handler(request: Request, exc: PyMongoError):
    return JSONResponse(
        status_code=503,
        content={"detail": "Database connection error. Please check if your IP is whitelisted in MongoDB Atlas."},
    )

def create_default_super_admin():
    try:
        admin = users_collection.find_one({"role": "SUPER_ADMIN"})
        if not admin:
            users_collection.insert_one(
                user_model(
                    username=SUPER_ADMIN_USERNAME,
                    email=SUPER_ADMIN_EMAIL,
                    password=hash_password(SUPER_ADMIN_PASSWORD),
                    role="SUPER_ADMIN"
                )
            )
            print("✅ Default Super Admin Created")
    except Exception as e:
        print(f"❌ Failed to create super admin: {e}")


# -------- INCLUDE ALL ROUTES --------
app.include_router(api_router)


@app.get("/")
def root():
    return {"message": "Backend running successfully"}
