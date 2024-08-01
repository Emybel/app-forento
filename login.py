import re
import bcrypt
import tkinter as tk
import customtkinter as ctk
from PIL import Image
from CTkMessagebox import CTkMessagebox
from helper import hash_password
# from setup_db.roles import get_forento_roles
from setup_db.db import db

def login_user(email, password):
    """ logs in an existing user."""

    if  not email or not password:
        CTkMessagebox(title="Missing Information", message="Please fill out all fields.")
        return None, None

    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        CTkMessagebox(title="Invalid Email", message="Please provide a valid email address.")
        return None, None

    email = email.strip().lower()
    users = db.users.find()  # This returns a cursor to all documents in the collection
    user = db.users.find_one({"email": email})
    # print(f"User credintials: {user}")
    
    if user:
        username = user["username"]
        stored_hashed_password = user["password"][0] # Get base64 string
        stored_salt = user["password"][1]
        
        # Re-hash the entered password using the stored salt
        rehashed_password = bcrypt.hashpw(password.encode(), salt=stored_salt)

        # Use bcrypt to check the password
        if rehashed_password == stored_hashed_password:
            logged_in_user_id = user["_id"]
            user_role = user["role"]
            return logged_in_user_id, user_role, username
        else:
            CTkMessagebox(title="Invalid Password", message="The provided password is incorrect.")
            return None, None, None     
    else:
        CTkMessagebox(title="User Not Found", message="The provided email and username combination does not exist.")
        return None, None, None
