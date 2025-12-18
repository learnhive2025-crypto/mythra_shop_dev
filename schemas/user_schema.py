from pydantic import BaseModel, EmailStr
# from pydantic import BaseModel, EmailStr
class LoginSchema(BaseModel):
    username: str
    password: str

class UserResponseSchema(BaseModel):
    id: str
    username: str
    email: str
    role: str




from pydantic import BaseModel, EmailStr
from typing import Optional


class AdminCreateSchema(BaseModel):
    username: str
    email: EmailStr
    password: str


class AdminUpdateSchema(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

    
class StaffCreateSchema(BaseModel):
    username: str
    email: EmailStr
    password: str


class StaffUpdateSchema(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
