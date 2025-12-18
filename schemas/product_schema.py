from pydantic import BaseModel, Field

class ProductCreateSchema(BaseModel):
    name: str = Field(..., example="Plastic Bucket")
    category_id: str = Field(..., example="693fcce4ce26b320c6436d64")
    purchase_price: float = Field(..., gt=0, example=120)
    selling_price: float = Field(..., gt=0, example=150)
    stock_qty: int = Field(0, ge=0, example=50)


class ProductUpdateSchema(BaseModel):
    name: str
    category_id: str
    purchase_price: float
    selling_price: float
    stock_qty: int
    is_active: bool

class ProductResponseSchema(BaseModel):
    id: str
    name: str
    barcode: str
    selling_price: float
    stock_qty: int
