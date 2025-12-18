from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from utils.security import get_current_user
import os

router = APIRouter(
    tags=["Excel"]
)

FILE_PATH = "product_barcodes.xlsx"

@router.get("/download-products")
def download_products_excel():
    if not os.path.exists(FILE_PATH):
        return {"error": "Excel file not found"}

    return FileResponse(
        path=FILE_PATH,
        filename="product_barcodes.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
