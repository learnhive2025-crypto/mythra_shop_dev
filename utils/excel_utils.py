import pandas as pd
import os

FILE_PATH = "product_barcodes.xlsx"

def append_product_to_excel(product: dict):
    columns = ["Product Name", "Category", "Barcode", "Selling Price"]

    if os.path.exists(FILE_PATH):
        df = pd.read_excel(FILE_PATH)
    else:
        df = pd.DataFrame(columns=columns)

    df.loc[len(df)] = [
        product["name"],
        product["category"],
        product["barcode"],
        product["selling_price"]
    ]

    df.to_excel(FILE_PATH, index=False)
