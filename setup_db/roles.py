from setup_db.db import db

def get_forento_roles():
    """Retrieves and returns a list of role names from the forento database."""
    roles_col = db.get_collection("roles")
    roles = [doc["role"] for doc in roles_col.find({}, {"_id": 0, "role": 1}).sort("role", 1)]
    return roles
