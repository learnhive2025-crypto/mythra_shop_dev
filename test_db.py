from pymongo import MongoClient
from pymongo.server_api import ServerApi
from config import MONGO_URL
import certifi
import sys

print("Testing MongoDB Connection...")
print(f"Python Version: {sys.version}")

try:
    print("Attempting to connect with certifi...")
    client = MongoClient(
        MONGO_URL,
        server_api=ServerApi("1"),
        tlsCAFile=certifi.where(),
        connectTimeoutMS=5000,
        serverSelectionTimeoutMS=5000
    )
    # The ismaster command is cheap and does not require auth.
    client.admin.command('ismaster')
    print("✅ Connection Successful!")
except Exception as e:
    print(f"❌ Connection Failed: {e}")

print("\n-----------------\n")

try:
    print("Attempting to connect with tlsAllowInvalidCertificates=True...")
    client = MongoClient(
        MONGO_URL,
        server_api=ServerApi("1"),
        tlsAllowInvalidCertificates=True,
        connectTimeoutMS=5000,
        serverSelectionTimeoutMS=5000
    )
    client.admin.command('ismaster')
    print("✅ Connection Successful (Insecure)!")
except Exception as e:
    print(f"❌ Connection Failed (Insecure): {e}")
