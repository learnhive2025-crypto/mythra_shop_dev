from datetime import datetime, timedelta

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from passlib.context import CryptContext

from config import SECRET_KEY, ALGORITHM

# ---------------- PASSWORD HASHING ----------------

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)


# ---------------- JWT TOKEN ----------------

def create_token(data: dict) -> str:
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(hours=8)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# ---------------- AUTH DEPENDENCY ----------------

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


# ---------------- ROLE BASED ACCESS ----------------

def super_admin_only(user: dict = Depends(get_current_user)):
    if user.get("role") != "SUPER_ADMIN":
        raise HTTPException(status_code=403, detail="Super Admin only")
    return user


def admin_or_super_admin(user: dict = Depends(get_current_user)):
    if user.get("role") not in ["ADMIN", "SUPER_ADMIN"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


def staff_only(user: dict = Depends(get_current_user)):
    if user.get("role") != "STAFF":
        raise HTTPException(status_code=403, detail="Staff only")
    return user
