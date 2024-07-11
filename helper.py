import bcrypt
from pymongo import MongoClient
from setup_db.db import db
from bson import ObjectId

salt = bcrypt.gensalt()
def hash_password(password, salt=salt):
    """Generates a hashed password using bcrypt."""
    
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password, salt

def create_user(username, hashed_password, email, role):
    """Create a new user in the forento.users collection."""
    user = {
        "username": username,
        "password": hashed_password,
        "email": email,
        "role": role
    }
    return db["users"].insert_one(user).inserted_id

def get_all_users():
    """Fetch all users from the forento.users collection."""
    users = db["users"].find()
    return list(users)

def check_email(email):
    """Check if the email already exists in the forento.users collection."""
    return db["users"].find_one({"email": email}) is not None

def delete_user(email):
    """Delete a user from the forento.users collection."""
    return db["users"].delete_one({"email": email})

def update_user( username, email, role):
    """Update a user's information in the forento.users collection."""
    update_fields = {"username": username, "email": email, "role": role}
    return db["users"].update_one({"email": email}, {"$set": update_fields})
