from pymongo import MongoClient
from urllib.parse import quote_plus

# Admin credentials (make sure to escape special characters if needed)
admin_username = quote_plus("Admin")
admin_password = quote_plus("ForentoAdmin1055")

# Connect to MongoDB with admin user
client = MongoClient(
    "mongodb://localhost:27017",
    username=admin_username,
    password=admin_password,
    authSource="forento",
    authMechanism="SCRAM-SHA-256",
)

db = client["forento"]