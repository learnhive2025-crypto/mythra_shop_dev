import truststore
import ssl
truststore.inject_into_ssl()

from pymongo import MongoClient
from pymongo.server_api import ServerApi
from config import MONGO_URL
import sys

print("Testing MongoDB Connection with truststore...")
print(f"Python Version: {sys.version}")

try:
    client = MongoClient(
        MONGO_URL,
        server_api=ServerApi("1"),
        connectTimeoutMS=5000,
        serverSelectionTimeoutMS=5000
    )
    # The ping command is cheap and does not require auth.
    client.admin.command('ping')
    print("✅ Connection Successful with truststore!")
except Exception as e:
    print(f"❌ Connection Failed with truststore: {e}")
