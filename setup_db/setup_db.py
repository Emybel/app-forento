from pymongo import MongoClient
import datetime

def setup_database():
    """
    This function sets up the MongoDB database for the Forento application.
    It creates the necessary collections, applies validation rules, and creates indexes.

    Parameters:
    None

    Returns:
    None
    """
    
    # Connect to MongoDB with authentication
    client = MongoClient('mongodb://Admin:ForentoAdmin1055@localhost:27017/forento')
    db = client.forento

    # Check if collections already exist
    collections = db.list_collection_names()

    if "users" not in collections:
        # Users collection schema and validation
        users_validator = {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["username", "password", "email", "role"],
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
        db.create_collection("users")
        db.command("collMod", "users", validator=users_validator)
        
        # Create unique indexes for username and email
        db.users.create_index("username", unique=True)
        db.users.create_index("email", unique=True)
        print("Users collection and indexes created.")
    else:
        print("Users collection already exists.")

    if "fly_detections" not in collections:
        # Detections collection schema and validation
        detections_validator = {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["date", "detections", "user_id"],
                "properties": {
                    
                    "date": {
                        "bsonType": "date",
                        "description": "must be a date and defaults to the current date"
                    },
                    "detections": {
                        "bsonType": "array",
                        "items": {
                            "bsonType": "object",
                            "required": ["time", "confidence", "image_path", "coordinates"],
                            "properties": {
                                "object_type": {
                                    "bsonType": "string",
                                    "description": "must be a string and is required"
                                },
                                "confidence": {
                                    "bsonType": "double",
                                    "description": "must be a double and is required"
                                },
                                "image_path": {
                                    "bsonType": "string",
                                    "description": "must be a string and is required"
                                },
                                "coordinates": {
                                    "bsonType": "object",
                                    "required": ["tl_x", "tl_y", "br_x", "br_y"],
                                    "properties": {
                                        "tl_x": {
                                            "bsonType": "double",
                                            "description": "must be a double and is required"
                                        },
                                        "tl_y": {
                                            "bsonType": "double",
                                            "description": "must be a double and is required"
                                        },
                                        "br_x": {
                                            "bsonType": "double",
                                            "description": "must be a double and is required"
                                        },
                                        "br_y": {
                                            "bsonType": "double",
                                            "description": "must be a double and is required"
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "user_id": {
                            "bsonType": "objectId",
                            "description": "must be an ObjectId and reference a user"
                    },
                }
            }
        }

        # Create detections collection with validation
        db.create_collection("fly_detections")
        db.command("collMod", "fly_detections", validator=detections_validator)
        print("Fly detections collection created.")
    else:
        print("Fly detections collection already exists.")

    if "roles" not in collections:
        # Create roles collection (for documentation purposes, not used by MongoDB natively)
        db.roles.insert_many([
            {"role": "Administrator", "description": "Full access to manage cases and users."},
            {"role": "Expert", "description": "Access to cases and detections related to their assigned cases."},
            {"role": "Technician", "description": "Read-only access to cases and detections they are assigned to."}
        ])
        print("Roles collection created.")
    else:
        print("Roles collection already exists.")

    print("Database setup completed.")
    


if __name__ == "__main__":
    setup_database()
