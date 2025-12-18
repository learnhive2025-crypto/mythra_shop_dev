# utils/barcode_utils.py
import random

def generate_barcode():
    return "89" + "".join(str(random.randint(0, 9)) for _ in range(11))
