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

def update_listbox(listbox, entries):
    """Update the listbox with new entries."""
    listbox.delete(0, tk.END)
    for entry in entries:
        listbox.insert(tk.END, entry["username"])

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("green")

    app = ctk.CTk()
    app.title("Case Management System")
    app.geometry("1200x900")

    # Main Frame
    main_frame = ctk.CTkFrame(app)
    main_frame.pack(padx=10, pady=10, fill="both", expand=True)
    
    header_frame = ctk.CTkFrame(main_frame, corner_radius=5)
    header_frame.pack(side="top", fill="x", padx=10)

    logo_image = ctk.CTkImage(Image.open("asset/logo.png"), size=(80, 80))

    app_name_label = ctk.CTkLabel(header_frame, text="FORENTO Fly Detector", font=("Arial", 20), anchor="center")
    logo_label = ctk.CTkLabel(header_frame, image=logo_image, text=" ", anchor='center')
    logo_label.pack(side="left", padx=40, pady=5)
    app_name_label.pack(side="left", pady=5)

    # Treeview for Cases
    columns = ("BSS Number", "Department Number", "Expert", "Technicians", "Status")
    
    case_treeview = ttk.Treeview(main_frame, columns=columns, show="headings", height=5)
    for col in columns:
        case_treeview.heading(col, text=col)
        case_treeview.column(col, minwidth=100, width=150, stretch=tk.NO)

    case_treeview.pack(padx=10, pady=10, fill="both", expand=True)
    scrollbar = ttk.Scrollbar(case_treeview, orient="vertical", command=case_treeview.yview)
    case_treeview.configure(yscroll=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    # Sub-frame for the Form
    form_frame = ctk.CTkFrame(main_frame)
    form_frame.pack(pady=10, fill="x")

    # Input Fields with Labels
    input_frame = ctk.CTkFrame(form_frame)
    input_frame.pack(pady=10, fill="x")

    ctk.CTkLabel(input_frame, text="BSS Number").pack(side="left", padx=5)
    bss_num_entry = ctk.CTkEntry(input_frame, placeholder_text="BSS Number")
    bss_num_entry.pack(side="left", padx=5, fill="x", expand=True)

    ctk.CTkLabel(input_frame, text="Department Number").pack(side="left", padx=5)
    dep_num_entry = ctk.CTkEntry(input_frame, placeholder_text="Department Number")
    dep_num_entry.pack(side="left", padx=5, fill="x", expand=True)

    ctk.CTkLabel(input_frame, text="Status").pack(side="left", padx=5)
    status_menu = ctk.CTkComboBox(input_frame, values=["open", "closed", "in_progress"])
    status_menu.pack(side="left", padx=5, fill="x", expand=True)

    # Assigned To and Technician IDs
    list_frame = ctk.CTkFrame(form_frame)
    list_frame.pack(pady=10, fill="x")

    ctk.CTkLabel(list_frame, text="Expert Assigned To").pack(side="left", padx=5)
    # assigned_to_entry = ctk.CTkEntry(list_frame, placeholder_text="Search and select")
    # assigned_to_entry.pack(side="left", padx=5, fill="x", expand=True)

    assigned_to_dropdown = ttk.Combobox(list_frame)
    assigned_to_dropdown.pack(side="left", padx=5, fill="x", expand=True)

    # Populate dropdowns
    assigned_to_dropdown['values'] = [entry["username"] for entry in get_usernames("Expert")]

    ctk.CTkLabel(list_frame, text="Technician IDs").pack(side="left", padx=5)
    # technician_ids_entry = ctk.CTkEntry(list_frame, placeholder_text="Search and select")
    # technician_ids_entry.pack(side="left", padx=5, fill="x", expand=True)

    technician_ids_listbox = tk.Listbox(list_frame, selectmode=tk.MULTIPLE, width=20)
    technician_ids_listbox.pack(pady=5, padx=5, fill="both", expand=True)

    # Populate listbox
    technician_ids_listbox.insert(tk.END, *[entry["username"] for entry in get_usernames("Technician")])


    # Variables to store selected user IDs
    assigned_to_id = None
    technician_ids_list = []

    # Refresh case list function
    def refresh_case_list():
        """Fetch cases from the database and display them in the treeview."""
        for row in case_treeview.get_children():
            case_treeview.delete(row)

        cases = get_all_cases()
        for case in cases:
            technicians = ", ".join(case["technician_usernames"])
            case_treeview.insert("", "end", values=(case["bss_num"], case["dep_num"], 
                                                    case["expert_username"], technicians, case["status"]))


    def create_new_case():
        """Creates a new case in the database."""
        bss_num = bss_num_entry.get()
        dep_num = dep_num_entry.get()
        status = status_menu.get()
        assigned_to = assigned_to_dropdown.get()
        # technician_ids = technician_ids_entry.get().split(",")

        if not bss_num.strip() or not dep_num.strip() or not status or not assigned_to.strip():
            CTkMessagebox(title="Missing Information", message="Please fill out all fields.")
            return

        try:
            create_case(bss_num, dep_num, status, assigned_to_id, technician_ids_list)
            CTkMessagebox(master=app, title="Success", message=f"Case '{bss_num}' created successfully!")
            bss_num_entry.delete(0, tk.END)
            dep_num_entry.delete(0, tk.END)
            # assigned_to_entry.delete(0, tk.END)
            # technician_ids_entry.delete(0, tk.END)
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
        status = status_menu.get()
        assigned_to = assigned_to_dropdown.get()
        # technician_ids = technician_ids_entry.get().split(",")

        if not bss_num.strip() or not dep_num.strip() or not status or not assigned_to.strip():
            CTkMessagebox(title="Missing Information", message="Please fill out all fields.")
            return

        try:
            update_case(case_id, bss_num, dep_num, status, assigned_to_id, technician_ids_list)
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
    
    # Buttons Frame
    button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    button_frame.pack(pady=10)

    create_btn = ctk.CTkButton(button_frame, text="Create Case", corner_radius=7, command=create_new_case)
    modify_btn = ctk.CTkButton(button_frame, text="Modify Case", corner_radius=7, command=modify_selected_case)
    delete_btn = ctk.CTkButton(button_frame, text="Delete Case", corner_radius=7, command=delete_selected_case)

    create_btn.pack(side="left", padx=10)
    modify_btn.pack(side="left", padx=10)
    delete_btn.pack(side="left", padx=10)

    def on_assigned_to_select(event):
        global assigned_to_id
        selected_user = assigned_to_dropdown.get()
        user = db.users.find_one({"username": selected_user}, {"_id": 1})
        assigned_to_id = user["_id"] if user else None

    def on_technician_select(event):
        global technician_ids_list
        selected_indices = technician_ids_listbox.curselection()
        selected_techs = [technician_ids_listbox.get(i) for i in selected_indices]
        technician_ids_list = [db.users.find_one({"username": tech.strip()}, {"_id": 1})["_id"] for tech in selected_techs if db.users.find_one({"username": tech.strip()}, {"_id": 1})]

    assigned_to_dropdown.bind("<<ComboboxSelected>>", on_assigned_to_select)
    technician_ids_listbox.bind("<<ListboxSelect>>", on_technician_select)


    def on_technician_select(event):
        global technician_ids_list
        selected_indices = technician_ids_listbox.curselection()
        selected_techs = [technician_ids_listbox.get(i) for i in selected_indices]
        technician_ids_list = [db.users.find_one({"username": tech.strip()}, {"_id": 1})["_id"] for tech in selected_techs if db.users.find_one({"username": tech.strip()}, {"_id": 1})]

    technician_ids_listbox.bind("<<ListboxSelect>>", on_technician_select)

    refresh_case_list()

    app.mainloop()