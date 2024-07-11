import re
import tkinter as tk
import customtkinter as ctk
from PIL import Image
from tkinter import ttk
from setup_db.db import db
from CTkMessagebox import CTkMessagebox
from bson import ObjectId
from datetime import datetime

def get_all_cases():
    """Fetch all cases from the database."""
    return list(db.cases.find())

def create_case(bss_num, dep_num, title, description, status, assigned_to, technician_ids):
    """Create a new case in the database."""
    case = {
        "bss_num": bss_num,
        "dep_num": dep_num,
        "title": title,
        "description": description,
        "created_at": datetime.utcnow(),
        "status": status,
        "assigned_to": ObjectId(assigned_to),
        "technician_ids": [ObjectId(tech_id) for tech_id in technician_ids]
    }
    return db.cases.insert_one(case).inserted_id

def update_case(case_id, bss_num, dep_num, title, description, status, assigned_to, technician_ids):
    """Update an existing case in the database."""
    update_fields = {
        "bss_num": bss_num,
        "dep_num": dep_num,
        "title": title,
        "description": description,
        "status": status,
        "assigned_to": ObjectId(assigned_to),
        "technician_ids": [ObjectId(tech_id) for tech_id in technician_ids]
    }
    db.cases.update_one({"_id": ObjectId(case_id)}, {"$set": update_fields})

def delete_case(case_id):
    """Delete a case from the database."""
    db.cases.delete_one({"_id": ObjectId(case_id)})

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("green")

    app = ctk.CTk()
    app.title("Case Management System")
    app.geometry("1200x900")

    header_frame = ctk.CTkFrame(app, corner_radius=5)
    header_frame.pack(side="top", fill="x", padx=10)

    logo_image = ctk.CTkImage(Image.open("asset/logo.png"), size=(80, 80))
    app_name_label = ctk.CTkLabel(header_frame, text="Case Management System", font=("Arial", 20), anchor="center")
    logo_label = ctk.CTkLabel(header_frame, image=logo_image, text=" ", anchor='center')
    logo_label.pack(side="left", padx=40, pady=5)
    app_name_label.pack(side="left", pady=5)

    form_frame = ctk.CTkFrame(app, corner_radius=5)
    form_frame.pack(padx=10, pady=10, fill="both", expand=True)

    label = ctk.CTkLabel(form_frame, text="Manage Case", font=("Roboto", 24))
    label.pack(pady=20, padx=10)

    bss_num_entry = ctk.CTkEntry(form_frame, placeholder_text="BSS Number")
    bss_num_entry.pack(pady=12, padx=10)

    dep_num_entry = ctk.CTkEntry(form_frame, placeholder_text="Department Number")
    dep_num_entry.pack(pady=12, padx=10)

    title_entry = ctk.CTkEntry(form_frame, placeholder_text="Title")
    title_entry.pack(pady=12, padx=10)

    description_entry = ctk.CTkEntry(form_frame, placeholder_text="Description")
    description_entry.pack(pady=12, padx=10)

    status_menu = ctk.CTkComboBox(form_frame, values=["open", "closed", "in_progress"])
    status_menu.pack(pady=12, padx=10)

    assigned_to_entry = ctk.CTkEntry(form_frame, placeholder_text="Assigned To (User ID)")
    assigned_to_entry.pack(pady=12, padx=10)

    technician_ids_entry = ctk.CTkEntry(form_frame, placeholder_text="Technician IDs (comma separated)")
    technician_ids_entry.pack(pady=12, padx=10)

    def refresh_case_list():
        """Fetch cases from the database and display them in the treeview."""
        for row in case_treeview.get_children():
            case_treeview.delete(row)
        
        cases = get_all_cases()
        for case in cases:
            case_treeview.insert("", "end", values=(case["_id"], case["bss_num"], case["dep_num"], case["title"], case["status"]))

    def create_new_case():
        """Creates a new case in the database."""
        bss_num = bss_num_entry.get()
        dep_num = dep_num_entry.get()
        title = title_entry.get()
        description = description_entry.get()
        status = status_menu.get()
        assigned_to = assigned_to_entry.get()
        technician_ids = technician_ids_entry.get().split(",")

        if not bss_num.strip() or not dep_num.strip() or not title.strip() or not status or not assigned_to.strip():
            CTkMessagebox(title="Missing Information", message="Please fill out all fields.")
            return

        try:
            create_case(bss_num, dep_num, title, description, status, assigned_to, technician_ids)
            CTkMessagebox(master=app, title="Success", message=f"Case '{title}' created successfully!")
            bss_num_entry.delete(0, tk.END)
            dep_num_entry.delete(0, tk.END)
            title_entry.delete(0, tk.END)
            description_entry.delete(0, tk.END)
            assigned_to_entry.delete(0, tk.END)
            technician_ids_entry.delete(0, tk.END)
            refresh_case_list()
        except Exception as e:
            CTkMessagebox(master=app, title="Error Creating Case", message=f"Error Creating Case: {e}")
            print(f"Error Creating Case: {e}")

    def modify_selected_case():
        """Modifies the selected case's information in the database."""
        selected_item = case_treeview.selection()
        if not selected_item:
            CTkMessagebox(master=app, title="Error", message="Please select a case to modify.")
            return

        case_id = case_treeview.item(selected_item, "values")[0]
        bss_num = bss_num_entry.get()
        dep_num = dep_num_entry.get()
        title = title_entry.get()
        description = description_entry.get()
        status = status_menu.get()
        assigned_to = assigned_to_entry.get()
        technician_ids = technician_ids_entry.get().split(",")

        if not bss_num.strip() or not dep_num.strip() or not title.strip() or not status or not assigned_to.strip():
            CTkMessagebox(title="Missing Information", message="Please fill out all fields.")
            return

        try:
            update_case(case_id, bss_num, dep_num, title, description, status, assigned_to, technician_ids)
            CTkMessagebox(master=app, title="Success", message="Case updated successfully!")
            refresh_case_list()
        except Exception as e:
            CTkMessagebox(master=app, title="Error", message=f"Error Updating Case: {e}")
            print(f"Error Updating Case: {e}")

    def delete_selected_case():
        """Deletes the selected case from the database."""
        selected_item = case_treeview.selection()
        if not selected_item:
            CTkMessagebox(master=app, title="Error", message="Please select a case to delete.")
            return

        case_id = case_treeview.item(selected_item, "values")[0]
        try:
            delete_case(case_id)
            CTkMessagebox(master=app, title="Success", message="Case deleted successfully!")
            refresh_case_list()
        except Exception as e:
            CTkMessagebox(master=app, title="Error", message=f"Error Deleting Case: {e}")
            print(f"Error Deleting Case: {e}")

    create_btn = ctk.CTkButton(form_frame, text="Create Case", corner_radius=7, command=create_new_case)
    create_btn.pack(pady=15)

    treeview_frame = ctk.CTkFrame(app, corner_radius=5)
    treeview_frame.pack(padx=10, pady=10, fill="both", expand=True)

    columns = ("ID", "BSS Number", "Department Number", "Title", "Status")
    case_treeview = ttk.Treeview(treeview_frame, columns=columns, show="headings", height=10)
    for col in columns:
        case_treeview.heading(col, text=col)
        case_treeview.column(col, minwidth=0, width=100, stretch=tk.NO)

    case_treeview.pack(padx=10, pady=10, fill="both", expand=True)
    scrollbar = ttk.Scrollbar(treeview_frame, orient="vertical", command=case_treeview.yview)
    case_treeview.configure(yscroll=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    button_frame = ctk.CTkFrame(app, corner_radius=5)
    button_frame.pack(pady=10)

    modify_btn = ctk.CTkButton(button_frame, text="Modify Case", corner_radius=7, command=modify_selected_case)
    modify_btn.pack(side="left", padx=10)

    delete_btn = ctk.CTkButton(button_frame, text="Delete Case", corner_radius=7, command=delete_selected_case)
    delete_btn.pack(side="left", padx=10)

    refresh_case_list()

    app.mainloop()
