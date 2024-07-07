import tkinter as tk
import customtkinter as ctk
from PIL import Image
from tkinter import ttk
from tkinter import filedialog
from CTkMessagebox import CTkMessagebox
import bcrypt
import datetime
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

# Fetch roles from the forento database
def get_forento_roles():
    """Retrieves and returns a list of role names from the forento database."""
    db = client["forento"]  # Connect to forento database
    roles_col = db.get_collection("system.roles")  # Access system.roles collection

    # Define the aggregation pipeline
    pipeline = [
        {"$project": {"_id": 0, "role": 1}},  # Project only the "role" field
        {"$sort": {"role": 1}},  # Sort roles alphabetically (optional)
    ]

    # Execute the aggregation and return role names
    roles = [doc["role"] for doc in roles_col.aggregate(pipeline)]
    return roles

roles = get_forento_roles()

def hash_password(password):
    """Generates a hashed password using bcrypt."""
    salt = bcrypt.gensalt()  # Generate a random salt
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password

def create_new_user():
    """Creates a new user in the forento database."""
    username = username_entry.get()
    password = pwd_entry.get()
    email = email_entry.get()
    selected_role = roles_menu.get()

    if not username or not password or not email or not selected_role:
        CTkMessagebox.show_error("Missing Information", "Please fill out all fields.")
        return

    hashed_password = hash_password(password)

    # Create user in forento.users collection
    try:
        db = client["forento"]
        users_col = db.get_collection("users")
        users_col.insert_one({
            "username": username,
            "password": hashed_password,
            "email": email,
            "roles": [selected_role],
            "created_at": datetime.datetime.utcnow()
        })
        CTkMessagebox.show_info("Success", f"User '{username}' created successfully!")
    except Exception as e:
        CTkMessagebox.show_error("Error Creating User", str(e))

if __name__ == "__main__":
    # Build GUI
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("green")

    app = ctk.CTk()

    app.title("Forento Fly Detector")
    app.geometry("480x900")

    # Header frame
    header_frame = ctk.CTkFrame(app, corner_radius=5)
    header_frame.pack(side="top", fill="x", padx=10)

    # Load logo image
    logo_image = ctk.CTkImage(Image.open("asset/logo.png"), size=(80, 80))

    # App name label
    app_name_label = ctk.CTkLabel(header_frame, text="FORENTO Fly Detector", font=("Arial", 20), anchor="center")
    logo_label = ctk.CTkLabel(header_frame, image=logo_image, text=" ", anchor='center')
    logo_label.pack(side="left", padx=40, pady=5)
    app_name_label.pack(side="left", pady=5)

    # Login frame
    login_frame = ctk.CTkFrame(app, corner_radius=5)
    login_frame.pack(padx=10, pady=10, fill="both", expand=True)

    # Auth frame
    auth_frame = ctk.CTkFrame(login_frame, border_width=1, border_color="#101c12", corner_radius=14)
    auth_frame.pack(padx=20, pady=20, fill="both", expand=True)

    label = ctk.CTkLabel(master=auth_frame, text="Create new user", font=("Roboto", 24))
    label.pack(pady=20, padx=10)

    # Fields to hold user data
    username_entry = ctk.CTkEntry(master=auth_frame, placeholder_text="Username")
    username_entry.pack(pady=12, padx=10)

    pwd_entry = ctk.CTkEntry(master=auth_frame, placeholder_text="Password", show="*")
    pwd_entry.pack(pady=12, padx=10)

    email_entry = ctk.CTkEntry(master=auth_frame, placeholder_text="example@outlook.com")
    email_entry.pack(pady=12, padx=10)

    # Role selection menu
    role_names = [role for role in roles]
    roles_menu = ctk.CTkComboBox(master=auth_frame, values=role_names)
    roles_menu.pack(pady=12, padx=10)

    # Create button
    create_btn = ctk.CTkButton(
        master=auth_frame,
        text="Create",
        corner_radius=7,
        command=create_new_user
    )
    create_btn.pack(pady=15)

    app.mainloop()

    # Close the connection
    client.close()