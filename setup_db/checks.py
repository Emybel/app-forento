from pymongo import MongoClient
from pymongo.errors import CollectionInvalid
import datetime

def check_schema():
    client = MongoClient('mongodb://Admin:ForentoAdmin1055@localhost:27017/forento')
    db = client.forento
    
    # Check users collection schema
    users_info = db.command("listCollections", filter={"name": "users"})
    print("Users Collection Schema:")
    print(users_info)
    
    # Check fly_detections collection schema
    detections_info = db.command("listCollections", filter={"name": "fly_detections"})
    print("Fly Detections Collection Schema:")
    print(detections_info)

# check_schema()



# Assuming you have a MongoClient instance `client` connected to your MongoDB server
client = MongoClient("mongodb://Admin:ForentoAdmin1055@localhost:27017/forento")
db = client["forento"]

# Define the validator for users collection
users_validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["username", "password", "email", "role", "created_at", "last_login"],
        "properties": {
            "username": {
                "bsonType": "string",
                "description": "must be a string and is required"
            },
            "password": {
                "bsonType": "string",
                "description": "must be a string and is required"
            },
            "email": {
                "bsonType": "string",
                "pattern": "^.+@.+\..+$",
                "description": "must be a valid email address and is required"
            },
            "role": {
                "bsonType": "string",
                "enum": ["Administrator", "Expert", "Technician"],
                "description": "must be a string and is required"
            },
            "created_at": {
                "bsonType": "date",
                "description": "must be a date and defaults to the current date"
            },
            "last_login": {
                "bsonType": "date",
                "description": "must be a date"
            }
        }
    }
}

# Create users collection with validation
try:
    db.create_collection("users", validator=users_validator)
    print("Users collection created with schema validation.")
except CollectionInvalid as e:
    print(f"Failed to create users collection: {e}")
