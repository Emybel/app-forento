from pymongo import MongoClient
import datetime

def setup_database():
    # Connect to MongoDB with authentication
    client = MongoClient('mongodb://Admin:ForentoAdmin1055@localhost:27017/forento')
    db = client.forento

    # Users collection schema and validation
    users_validator = {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["username", "password", "email"],
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
    print("Unique indexes created.")

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

    print("Database setup completed.")

if __name__ == "__main__":
    setup_database()