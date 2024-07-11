
import datetime
from pymongo import MongoClient
from bson import ObjectId

client = MongoClient('mongodb://localhost:27017', username="Admin", password="ForentoAdmin1055", authSource="forento", authMechanism="SCRAM-SHA-256")
db = client["forento"]

# Utility function to get a user's role
def get_user_role(user_id):
    user = db.users.find_one({"_id": ObjectId(user_id)})
    return user["role"] if user else None

# Check is user exists
def check_email(email):
    user = db.users.find_one({"email": email})
    return user is not None

# Administrator Actions
def create_user(username, hashed_password, email, role):
    last_login = datetime.datetime.utcnow()
    if role not in ["Administrator", "Expert", "Technician"]:
        raise ValueError("Invalid role")
    
    user = {
        "username": username,
        "password": {
            "hashed_pwd": hashed_password
            },
        "email": email,
        "role": role,
        "created_at": datetime.datetime.utcnow(),  # Set created_at to current UTC time
        "last_login": last_login  # Initialize last_login to None
    }
    result = db.users.insert_one(user)
    return result.inserted_id

def delete_user(user_id):
    result = db.users.delete_one({"_id": ObjectId(user_id)})
    return result.deleted_count

def update_user(user_id, updates):
    result = db.users.update_one({"_id": ObjectId(user_id)}, {"$set": updates})
    return result.modified_count

def assign_case(case_id, expert_id):
    result = db.cases.update_one({"_id": ObjectId(case_id)}, {"$set": {"expert_id": ObjectId(expert_id)}})
    return result.modified_count

def create_case(case_data):
    case_data["created_at"] = datetime.datetime.utcnow()
    result = db.cases.insert_one(case_data)
    return result.inserted_id

def delete_case(case_id):
    result = db.cases.delete_one({"_id": ObjectId(case_id)})
    return result.deleted_count

def update_case(case_id, updates):
    result = db.cases.update_one({"_id": ObjectId(case_id)}, {"$set": updates})
    return result.modified_count

def view_all_cases():
    cases = list(db.cases.find())
    return cases

# Expert Actions
def view_assigned_cases(expert_id):
    cases = list(db.cases.find({"expert_id": ObjectId(expert_id)}))
    return cases

def create_case_by_expert(case_data, expert_id):
    case_data["expert_id"] = ObjectId(expert_id)
    case_data["created_at"] = datetime.datetime.utcnow()
    result = db.cases.insert_one(case_data)
    return result.inserted_id

def assign_technician(case_id, technician_id):
    result = db.cases.update_one({"_id": ObjectId(case_id)}, {"$push": {"technicians": ObjectId(technician_id)}})
    return result.modified_count

def search_cases(query):
    cases = list(db.cases.find(query))
    return cases

def filter_cases(filters):
    cases = list(db.cases.find(filters))
    return cases

# Technician Actions
def view_assigned_cases_for_technician(technician_id):
    cases = list(db.cases.find({"technicians": ObjectId(technician_id)}))
    return cases

def search_cases_for_technician(query):
    cases = list(db.cases.find(query))
    return cases

def filter_cases_for_technician(filters):
    cases = list(db.cases.find(filters))
    return cases

