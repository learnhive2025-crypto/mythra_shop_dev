from datetime import datetime

def product_model(
    name,
    category_id,
    purchase_price,
    selling_price,
    barcode,
    stock_qty=0,
    is_active=True
):
    return {
        "name": name,
        "category_id": category_id,
        "purchase_price": purchase_price,
        "selling_price": selling_price,
        "barcode": barcode,          # ✅ AUTO GENERATED
        "stock_qty": stock_qty,
        "is_active": is_active,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
