import tkinter as tk
import re
import customtkinter as ctk
from PIL import Image
from CTkMessagebox import CTkMessagebox
from actions import create_user, hash_password, salt, check_email
from setup_db.roles import get_forento_roles
from setup_db.db import db

roles = get_forento_roles()
print(f"list of roles: {roles}")

def destroy_login_window_and_show_main_window():
    """Destroys the login window and shows the main window."""
    app.destroy()
    # Import the main app here to avoid circular imports
    from mongodb import app # noqa
    app.start_app()

def create_new_user():
    """Creates a new user in the forento database."""
    username = username_entry.get()
    password = pwd_entry.get()
    email = email_entry.get()
    selected_role = roles_menu.get()

    print(f"Username: {username}")
    print(f"Password: {password}")
    print(f"Email: {email}")
    print(f"Selected Role: {selected_role}")
    
    if not username.strip() or not password.strip() or not email.strip() or not selected_role:
        CTkMessagebox(title="Missing Information", message="Please fill out all fields.")
        return
    
    if check_email(email):
        CTkMessagebox(title="Email already exists", message="This email is already used by another user. Please give another email adress.")
        return

    try:
        hashed_password= hash_password(password)
        print(f"hashed password: {hashed_password}")
        # print(f"hashed password: {salt}")
    except Exception as e:
        CTkMessagebox(master=app, title="Error", message="An error occurred while hashing the password.")
        print(f"Error hashing password: {e}")
        return

    # Create user in forento.users collection
    try:
        user_id = create_user(username, hashed_password, email, selected_role)
        CTkMessagebox(master=app, title="Success", message=f"User '{username}' created successfully!")
        # Clear the fields
        username_entry.delete(0, tk.END)
        pwd_entry.delete(0, tk.END)
        email_entry.delete(0, tk.END)
    except Exception as e:
        CTkMessagebox(master=app, title="Error Creating User", message=f"Error Creating User")
        print(f"Error Creating User: {e}")

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("green")

    app = ctk.CTk()
    app.title("Forento Fly Detector")
    app.geometry("480x900")

    header_frame = ctk.CTkFrame(app, corner_radius=5)
    header_frame.pack(side="top", fill="x", padx=10)

    logo_image = ctk.CTkImage(Image.open("asset/logo.png"), size=(80, 80))

    app_name_label = ctk.CTkLabel(header_frame, text="FORENTO Fly Detector", font=("Arial", 20), anchor="center")
    logo_label = ctk.CTkLabel(header_frame, image=logo_image, text=" ", anchor='center')
    logo_label.pack(side="left", padx=40, pady=5)
    app_name_label.pack(side="left", pady=5)

    register_frame = ctk.CTkFrame(app, corner_radius=5)
    register_frame.pack(padx=10, pady=10, fill="both", expand=True)

    auth_frame = ctk.CTkFrame(register_frame, border_width=1, border_color="#101c12", corner_radius=14)
    auth_frame.pack(padx=20, pady=20, fill="both", expand=True)

    label = ctk.CTkLabel(master=auth_frame, text="Create new user", font=("Roboto", 24))
    label.pack(pady=20, padx=10)

    username_entry = ctk.CTkEntry(master=auth_frame, placeholder_text="Username")
    username_entry.pack(pady=12, padx=10)

    pwd_entry = ctk.CTkEntry(master=auth_frame, placeholder_text="Password", show="*")
    pwd_entry.pack(pady=12, padx=10)

    email_entry = ctk.CTkEntry(master=auth_frame, placeholder_text="example@outlook.com")
    email_entry.pack(pady=12, padx=10)

    role_names = [role for role in roles]
    roles_menu = ctk.CTkComboBox(master=auth_frame, values=role_names)
    roles_menu.pack(pady=12, padx=10)

    create_btn = ctk.CTkButton(
        master=auth_frame,
        text="Create User",
        corner_radius=7,
        command=create_new_user
    )
    create_btn.pack(pady=15)

    app.mainloop()