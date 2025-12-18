from datetime import datetime

def purchase_model(
    invoice_no: str,
    supplier_name: str,
    items: list,
    total_amount: float
):
    return {
        "invoice_no": invoice_no,
        "supplier_name": supplier_name,
        "items": items,              # [{product_id, qty, price}]
        "total_amount": total_amount,
        "created_at": datetime.utcnow()
    }
