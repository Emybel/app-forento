import re
import tkinter as tk
import customtkinter as ctk
from PIL import Image
from tkinter import ttk
from setup_db.db import db
from CTkMessagebox import CTkMessagebox
from setup_db.roles import get_forento_roles
from helper import create_user, hash_password, check_email, get_all_users, update_user, delete_user

roles = get_forento_roles()
print(f"list of roles: {roles}")

def refresh_user_list():
    """Fetch users from the database and display them in the treeview."""
    for row in user_treeview.get_children():
        user_treeview.delete(row)
    
    users = get_all_users()
    for user in users:
        user_treeview.insert("", "end", values=(user["username"], user["email"], user["role"]))

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
        refresh_user_list()
    except Exception as e:
        CTkMessagebox(master=app, title="Error Creating User", message=f"Error Creating User")
        print(f"Error Creating User: {e}")
        
def modify_selected_user():
    """Modifies the selected user's information in the database."""
    selected_item = user_treeview.selection()
    if not selected_item:
        CTkMessagebox(master=app, title="Error", message="Please select a user to modify.")
        return
    
    current_email = user_treeview.item(selected_item, "values")[1]
    username = username_entry.get().strip()
    new_email = email_entry.get().strip()
    pwd = pwd_entry.get().strip()
    selected_role = roles_menu.get().strip()

    if not username and not new_email and not pwd and not selected_role:
        CTkMessagebox(title="Missing Information", message="Please fill out at least one field.")
        return

    try:
        update_user(current_email, username if username else None, new_email if new_email else None, selected_role if selected_role else None, pwd if pwd else None)
        CTkMessagebox(master=app, title="Success", message="User updated successfully!")
        refresh_user_list()
    except ValueError as ve:
        CTkMessagebox(master=app, title="Error", message=str(ve))
    except Exception as e:
        CTkMessagebox(master=app, title="Error", message=f"Error Updating User")
        print(f"Error Updating User: {e}")

def delete_selected_user():
    """Deletes the selected user from the database."""
    selected_item = user_treeview.selection()
    if not selected_item:
        CTkMessagebox(master=app, title="Error", message="Please select a user to delete.")
        return
    
    email = user_treeview.item(selected_item, "values")[1]
    try:
        delete_user(email)
        CTkMessagebox(master=app, title="Success", message="User deleted successfully!")
        refresh_user_list()
    except Exception as e:
        CTkMessagebox(master=app, title="Error", message=f"Error Deleting User")
        print(f"Error Deleting User: {e}")

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("green")

    app = ctk.CTk()
    app.title("Forento Fly Detector")
    app.geometry("1100x850")
    
    # Main Frame
    main_frame = ctk.CTkFrame(app)
    main_frame.pack(padx=10, pady=10, fill="both", expand=True)

    # Header
    header_frame = ctk.CTkFrame(main_frame, corner_radius=5)
    header_frame.pack(side="top", fill="x", padx=10)

    logo_image = ctk.CTkImage(Image.open("asset/logo.png"), size=(80, 80))

    app_name_label = ctk.CTkLabel(header_frame, text="FORENTO Fly Detector", font=("Arial", 20), anchor="center")
    logo_label = ctk.CTkLabel(header_frame, image=logo_image, text=" ", anchor='center')
    logo_label.pack(side="left", padx=40, pady=5)
    app_name_label.pack(side="left", pady=5)

    # Add a frame for the treeview
    treeview_frame = ctk.CTkFrame(main_frame, corner_radius=5)
    treeview_frame.pack(padx=10, pady=10, fill="both", expand=True)

    # Add a treeview to display users
    columns = ("Username", "Email", "Role")
    user_treeview = ttk.Treeview(treeview_frame, columns=columns, show="headings", height=10)
    for col in columns:
        user_treeview.heading(col, text=col)
        user_treeview.column(col, minwidth=100, width=150, stretch=tk.NO)

    user_treeview.pack(padx=10, pady=10, fill="both", expand=True)
    scrollbar = ttk.Scrollbar(user_treeview, orient="vertical", command=user_treeview.yview)
    user_treeview.configure(yscroll=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    # Add form to manage users data
    form_frame = ctk.CTkFrame(main_frame, corner_radius=5)
    form_frame.pack(padx=10, pady=10, fill="x", expand=True)

    auth_frame = ctk.CTkFrame(form_frame, border_width=1, border_color="#101c12", corner_radius=14)
    auth_frame.pack(padx=20, pady=10, fill="x", expand= True)

    sub_frame1 = ctk.CTkFrame(auth_frame, fg_color="transparent", width=100)
    sub_frame2 = ctk.CTkFrame(auth_frame, fg_color="transparent", width= 100)
    
    ctk.CTkLabel(auth_frame, text="Manage users", font=("Roboto", 24)).pack(side="top", padx=5, pady= 10)
    sub_frame1.pack(padx=10, pady=5)
    sub_frame2.pack(padx=10, pady=5)
        

    ctk.CTkLabel(sub_frame1, text="Full name:").pack(side="left", padx=5, pady= 20)
    username_entry = ctk.CTkEntry(sub_frame1, placeholder_text="Full name")
    username_entry.pack(side="left", padx=5, pady= 10, fill="x", expand=True)

    ctk.CTkLabel(sub_frame1, text="Password:").pack(side="left", padx=5, pady= 20)
    pwd_entry = ctk.CTkEntry(sub_frame1, placeholder_text="Password", show="*")
    pwd_entry.pack(side="left", padx=5, pady= 10, fill="x", expand=True)

    ctk.CTkLabel(sub_frame2, text="Email:").pack(side="left", padx=5, pady= 20)
    email_entry = ctk.CTkEntry(sub_frame2, placeholder_text="example@outlook.com")
    email_entry.pack(side="left", padx=5, pady= 10, fill="x", expand=True)

    ctk.CTkLabel(sub_frame2, text="Role:").pack(side="left", padx=5, pady= 20)
    role_names = [role for role in roles]
    roles_menu = ctk.CTkComboBox(sub_frame2, values=role_names)
    roles_menu.pack(side="left", padx=5, pady= 10, fill="x", expand=True)

    # Buttons Frame
    button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    button_frame.pack(pady=20)

    create_btn = ctk.CTkButton(
        master=button_frame,
        text="Create User",
        corner_radius=7,
        command=create_new_user
    )

    modify_btn = ctk.CTkButton(
        master=button_frame,
        text="Modify User",
        corner_radius=7,
        command=modify_selected_user
    )

    delete_btn = ctk.CTkButton(
        master=button_frame,
        text="Delete User",
        corner_radius=7,
        command= delete_selected_user
    )
    
    create_btn.pack(side="left", padx=10)
    modify_btn.pack(side="left", padx=10)
    delete_btn.pack(side="left", padx=10)

    refresh_user_list()

    app.mainloop()