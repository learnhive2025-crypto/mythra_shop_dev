from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from utils.security import get_current_user
from database import db
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

router = APIRouter(
    prefix="/export",
    tags=["Export"]
)

products_collection = db["products"]

# ---------------- EXPORT STOCK TO EXCEL ----------------
@router.get("/stock/excel")
def export_stock_excel(user=Depends(get_current_user)):
    data = []

    for p in products_collection.find({"is_active": True}):
        data.append({
            "Product": p["name"],
            "Stock": p["stock_qty"],
            "Selling Price": p["selling_price"]
        })

    df = pd.DataFrame(data)
    file_path = "stock_report.xlsx"
    df.to_excel(file_path, index=False)

    return FileResponse(
        file_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename="stock_report.xlsx"
    )

# ---------------- EXPORT STOCK TO PDF ----------------
@router.get("/stock/pdf")
def export_stock_pdf(user=Depends(get_current_user)):
    file_path = "stock_report.pdf"
    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4

    y = height - 40
    c.drawString(40, y, "Stock Report")
    y -= 30

    for p in products_collection.find({"is_active": True}):
        c.drawString(40, y, f"{p['name']} - Stock: {p['stock_qty']}")
        y -= 20

        if y < 40:
            c.showPage()
            y = height - 40

    c.save()
    return FileResponse(file_path, filename="stock_report.pdf")
