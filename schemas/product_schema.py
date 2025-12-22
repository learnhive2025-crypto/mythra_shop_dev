from pydantic import BaseModel, Field
from typing import Optional

class ProductCreateSchema(BaseModel):
    name: str = Field(..., example="Plastic Bucket")
    category_id: str = Field(..., example="693fcce4ce26b320c6436d64")
    purchase_price: float = Field(..., gt=0, example=120)
    selling_price: float = Field(..., gt=0, example=150)
    stock_qty: int = Field(0, ge=0, example=50)


class ProductUpdateSchema(BaseModel):
    name: Optional[str] = None
    category_id: Optional[str] = None
    purchase_price: Optional[float] = None
    selling_price: Optional[float] = None
    stock_qty: Optional[int] = None
    is_active: Optional[bool] = None

class ProductResponseSchema(BaseModel):
    id: str
    name: str
    barcode: str
    selling_price: float
    stock_qty: int
