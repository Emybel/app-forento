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

def get_forento_roles():
    """Retrieves and returns a list of role names from the forento database."""
    roles_col = db.get_collection("roles")
    roles = [doc["role"] for doc in roles_col.find({}, {"_id": 0, "role": 1}).sort("role", 1)]
    return roles

def close_connection():
    client.close()
