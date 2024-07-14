import bcrypt
from pymongo import MongoClient
from setup_db.db import db
from bson import ObjectId
from datetime import datetime
"""
---------- HELPER FUNCTIONS FOR USER MANAGEMENT ----------

"""
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

def update_user(email, username=None, new_email=None, role=None, password=None):
    """Update a user's information in the forento.users collection."""
    update_fields = {}
    
    if username:
        update_fields["username"] = username
    if new_email:
        update_fields["email"] = new_email
    if role:
        update_fields["role"] = role
    if password:
        pwd = hash_password(password)
        update_fields["password"] = pwd
    
    if update_fields:
        return db["users"].update_one({"email": email}, {"$set": update_fields})
    else:
        raise ValueError("No fields to update.")

"""
---------- HELPER FUNCTIONS FOR CASE MANAGEMENT ----------

"""

def create_case(bss_num, dep_num, status, assigned_to, technician_ids):
    """Create a new case in the database."""
    case = {
        "bss_num": bss_num,
        "dep_num": dep_num,
        "created_at": datetime.utcnow(),
        "status": status,
        "assigned_to": ObjectId(assigned_to),
        "technician_ids": [ObjectId(tech_id) for tech_id in technician_ids]
    }
    return db.cases.insert_one(case).inserted_id

def update_case(case_id, bss_num, dep_num, status, assigned_to, technician_ids):
    """Update an existing case in the database."""
    update_fields = {
        "bss_num": bss_num,
        "dep_num": dep_num,
        "status": status,
        "assigned_to": ObjectId(assigned_to),
        "technician_ids": [ObjectId(tech_id) for tech_id in technician_ids]
    }
    db.cases.update_one({"_id": ObjectId(case_id)}, {"$set": update_fields})
    
def delete_case(case_id):
    """Delete a case from the database."""
    db.cases.delete_one({"_id": ObjectId(case_id)})

def search_users(search_text):
    """Search for users whose username matches the search text."""
    return list(db.users.find({"username": {"$regex": search_text, "$options": "i"}}, {"_id": 1, "username": 1}))

def update_dropdown(dropdown, entries):
    """Update the dropdown with new entries."""
    dropdown['values'] = [entry["username"] for entry in entries]
    if entries:
        dropdown.current(0)
    else:
        dropdown.set("")

