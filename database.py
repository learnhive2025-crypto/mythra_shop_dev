from pymongo import MongoClient
from pymongo.server_api import ServerApi
from config import MONGO_URL, DB_NAME
import certifi

# MongoDB Client (Atlas/Local)
# Added tlsCAFile to support Atlas connections with certifi
client = MongoClient(
    MONGO_URL,
    tlsCAFile=certifi.where()
)

db = client[DB_NAME]

users_collection = db["users"]
products_collection = db["products"]
categories_collection = db["categories"]
