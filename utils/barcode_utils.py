# utils/barcode_utils.py
import random

def generate_barcode():
    return "" + "".join(str(random.randint(0, 9)) for _ in range(4))

def generate_unique_barcode(collection):
    while True:
        barcode = generate_barcode()
        if not collection.find_one({"barcode": barcode}):
            return barcode

