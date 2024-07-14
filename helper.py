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
def get_all_cases():
    """Fetch all cases from the database and include usernames for assigned Expert and Technicians."""
    cases = list(db.cases.find())
    for case in cases:
        # Fetch the expert's username
        expert = db.users.find_one({"_id": case["assigned_to"]})
        case["expert_username"] = expert["username"] if expert else "Unknown"
        
        # Fetch technician usernames
        technicians = db.users.find({"_id": {"$in": case["technician_ids"]}})
        case["technician_usernames"] = [tech["username"] for tech in technicians]
        
    return cases

def get_usernames(role=None):
    """Fetch usernames from the database, optionally filtering by role."""
    query = {}
    if role:
        query = {"role": role}
    return list(db.users.find(query, {"_id": 1, "username": 1}))

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

def update_case(bss_num, update_fields):
    """Update an existing case in the database."""
    try:
        result = db.cases.update_one({"bss_num": bss_num}, {"$set": update_fields})
        if result.matched_count == 0:
            raise ValueError("No case found with the provided BSS number.")
        if result.modified_count == 0:
            print("No fields were modified.")
    except Exception as e:
        print(f"Error updating case in database: {e}")
        raise
def delete_case(case_bss_num):
    """Delete a case from the database."""
    db.cases.delete_one({"bss_num":case_bss_num })

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

