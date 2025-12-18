from datetime import datetime

def sales_model(
    bill_no: str,
    items: list,
    total_amount: float,
    payment_mode: str,
    created_by: str
):
    """
    Barcode-based Sales Model
    items format:
    [
      {
        product_id,
        barcode,
        qty,
        price
      }
    ]
    """
    return {
        "bill_no": bill_no,
        "items": items,               # ✅ barcode included
        "total_amount": total_amount,
        "payment_mode": payment_mode, # Cash / UPI / Card
        "created_by": created_by,     # staff/admin user_id
        "created_at": datetime.utcnow()
    }
