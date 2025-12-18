from pydantic import BaseModel

class CategoryCreateSchema(BaseModel):
    name: str

class CategoryUpdateSchema(BaseModel):
    name: str
    is_active: bool
