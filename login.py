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
    # print(f"email: {email}")
    # print(f"password: {password}")
    
    users = db.users.find()  # This returns a cursor to all documents in the collection
    # for user in users:
    #     print(user)
    
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

# if __name__ == "__main__":
#     ctk.set_appearance_mode("dark")
#     ctk.set_default_color_theme("green")

#     login_window = ctk.CTk()
#     login_window.title("Forento Fly Detector")
#     login_window.geometry("480x900")

#     header_frame = ctk.CTkFrame(login_window, corner_radius=5)
#     header_frame.pack(side="top", fill="x", padx=10)

#     logo_image = ctk.CTkImage(Image.open("asset/logo.png"), size=(80, 80))

#     app_name_label = ctk.CTkLabel(header_frame, text="FORENTO Fly Detector", font=("Arial", 20), anchor="center")
#     logo_label = ctk.CTkLabel(header_frame, image=logo_image, text=" ", anchor='center')
#     logo_label.pack(side="left", padx=40, pady=5)
#     app_name_label.pack(side="left", pady=5)

#     login_frame = ctk.CTkFrame(login_window, corner_radius=5)
#     login_frame.pack(padx=10, pady=10, fill="both", expand=True)

#     auth_frame = ctk.CTkFrame(login_frame, border_width=1, border_color="#101c12", corner_radius=14)
#     auth_frame.pack(padx=20, pady=20, fill="both", expand=True)

#     label = ctk.CTkLabel(master=auth_frame, text="Login", font=("Roboto", 24))
#     label.pack(pady=20, padx=10)

#     email_entry = ctk.CTkEntry(master=auth_frame, placeholder_text="example@outlook.com")
#     email_entry.pack(pady=12, padx=10)

#     pwd_entry = ctk.CTkEntry(master=auth_frame, placeholder_text="Password", show="*")
#     pwd_entry.pack(pady=12, padx=10)

#     login_btn = ctk.CTkButton(
#         master=auth_frame,
#         text="Login",
#         corner_radius=7,
#         command=login_user
#     )
#     login_btn.pack(pady=15)

#     login_window.mainloop()