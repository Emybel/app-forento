import os
import PIL
import sys
import pymongo
import cv2 as cv
import tkinter as tk
from tkinter import ttk
from tkinter import *
from CTkTable import *
import customtkinter as ctk
from PIL import Image, ImageTk
from CTkMessagebox import CTkMessagebox

# Function to connect to MongoDB database
def connect_to_db():
    client = pymongo.MongoClient("mongodb://localhost:27017/")  # Replace with your connection string
    db = client["forento"]  # Replace "forento" with your database name
    case_collection = db["cases"]  # Replace "cases" with your collection name
    user_collection = db["users"]  # Replace "users" with your collection name
    return case_collection, user_collection

# Function to retrieve user list
def get_user_list(user_collection):
    users = list(user_collection.find({}, {"_id": 0, "full_name": 1}))  # Project full names only
    return [user["full_name"] for user in users]

# Custom function to check if an external camera is available
def check_external_camera():
    external_cameras = []
    for i in range(5):
        cap = cv.VideoCapture(i)
        if cap.isOpened():
            if not is_built_in_webcam(cap):
                external_cameras.append(cap)
            else:
                cap.release()
    
    if len(external_cameras) > 1:
        print(f"Found {len(external_cameras)} external cameras")
        return external_cameras[1]
    else:
        print("No external camera found")
        return None

# Helper function to check if a camera is a built-in webcam
def is_built_in_webcam(cap):
    # Check the camera name or other properties to determine if it's a built-in webcam
    # This implementation assumes that built-in webcams have "webcam" in their name
    cap_name = cap.getBackendName()
    return "webcam" in cap_name.lower()

# Function to prompt for save directory
def get_save_directory():
    folder_path = filedialog.askdirectory(title="Select Save Directory")
    if folder_path:
        print(f"Selected save directory: {folder_path}")
        return folder_path
    else:
        return None

def exit_program():
    """Performs cleanup tasks and exits the program."""
    global cap, fly_data_file, running

    # Close the camera capture (if open)
    if cap:
        cap.release()

    # Set a flag to stop the main loop (if applicable)
    running = False

    # Exit the program
    sys.exit()  # Import the `sys` module if not already imported

def ask_question():
    msg = CTkMessagebox(title="Exit", 
                        message="Do you want to close the program?", 
                        icon="question",  
                        option_1="Yes", 
                        option_2="No")
    
    response = msg.get()
    
    if response == "Yes":
        # Call a function to handle cleanup and program termination
        exit_program()
    else:
        print("Operation canceled.")

def login():
    return print ("Login successfully")

class CaseManager(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master

        # Create table frame
        self.table_frame = ctk.CTkFrame(self)
        self.table_frame.pack(pady=10, padx=10, fill="both")

        # Scrollbar
        self.tree_scroll = ttk.Scrollbar(self.table_frame)
        self.tree_scroll.pack(side="right", fill="y")

        # Table data (headers included for new rows)
        self.table_data = [["Select", "id_case", "BSS N°", "DEP N°", "Chargés d'affaire", "Saved Detections"]]

        # Create CTkTable
        self.table = CTkTable(self.table_frame, columns=self.table_data[0], show="headings", yscrollcommand=self.tree_scroll.set)
        for col, heading in enumerate(self.table_data[0]):
            self.table.heading(col, text=heading)
            self.table.column(col, width=120 if heading != "Select" else 40)  # Adjust column widths
        self.table.pack(expand=True, fill="both", padx=20, pady=10)
        self.tree_scroll.config(command=self.table.yview)

        # Create frame for buttons
        self.manage_btn_frame = ctk.CTkFrame(self)
        self.manage_btn_frame.pack(pady=10, padx=10)

        # Create buttons
        self.add_case_btn = ctk.CTkButton(self.manage_btn_frame, text="+", command=self.add_case, width=2, height=2, font=("Roboto", 20))
        self.add_case_btn.pack(expand=True, fill="both", padx=10, pady=10, side=tk.LEFT)

        self.rmv_case_btn = ctk.CTkButton(self.manage_btn_frame, text="-", command=self.remove_case, width=2, height=2, font=("Roboto", 20), state=tk.DISABLED)
        self.rmv_case_btn.pack(expand=True, fill="both", padx=10, pady=10, side=tk.LEFT)

        self.modify_case_btn = ctk.CTkButton(self.manage_btn_frame, text="modify", command=self.modify_case, state=tk.DISABLED)
        self.modify_case_btn.pack(expand=True, fill="both", padx=10, pady=10, side=tk.LEFT)

        # Additional variables for new row data
        self.bss_number_var = tk.StringVar(self)
        self.dep_number_var = tk.StringVar(self)
        self.selected_row = None

        def add_case(self):
            # Get user list from database
            case_collection, user_collection = connect_to_db()
            user_list = get_user_list(user_collection)

            # Update dropdown options
            self.user_var.set("")  # Clear selection
            self.user_dropdown["menu"].delete(0, tk.END)  # Clear existing options
            for user in user_list:
                self.user_dropdown["menu"].add_command(label=user, command=lambda user_name=user: self.user_var.set(user_name))

            # Prompt for BSS and DEP numbers (replace with your preferred dialog)
            bss_number = tk.simpledialog.askstring("BSS Number", "Enter BSS number (12 characters):")
            dep_number = tk.simpledialog.askstring("DEP Number", "Enter DEP number (5 characters):")

            if bss_number and len(bss_number) == 12 and dep_number and len(dep_number) == 5:
                # Validate BSS and DEP numbers (add your validation logic here)
                new_row = ["-", None, bss_number.strip(), dep_number.strip(), self.user_var.get(), ""]
                self.table.insert("", tk.END, values=new_row)
                
        def remove_case(self):
            if self.selected_row:
                self.table.delete(self.selected_row)
                self.selected_row = None  # Clear selection

        def modify_case(self):
            if self.selected_row:
                # Get current values from the table
                selected_values = self.table.item(self.selected_row)["values"]

                # Prompt for modifications (replace with your preferred dialog)
                # ... (similar to add_case logic)

                # Update the table with modified values

        def save_case(self):
            case_collection, _ = connect_to_db()

            # Get data from the selected row (assuming a single selection)
            selected_row = self.table.selection()
            if not selected_row:
                print("No row selected. Please select a case to save.")
                return

            # Extract data from the selected row
            selected_data = self.table.get_row(selected_row[0])

            # Validate data (optional)
            # You can add checks for empty fields or data format here

            # Prepare data for database insertion
            case_data = {
                "BSS_number": selected_data[2],  # Assuming BSS number is at index 2
                "DEP_number": selected_data[3],  # Assuming DEP number is at index 3
                "assigned_user": selected_data[4],  # Assuming assigned user is at index 4
                "saved_detections": [],  # Empty list for saved detections (replace if needed)
            }

            # Insert data into the database
            case_collection.insert_one(case_data)

            print(f"Case saved successfully! (BSS: {case_data['BSS_number']}, DEP: {case_data['DEP_number']})")


            # Insert data into database
            case_collection.insert_one(case_data)

            # Update table with generated ID
            self.table.set(row, column="id_case", value=case_id)
            self.table.set(row, column="Select", value="")  # Clear checkbox

        def select_row(self, event):
            self.selected_row = self.table.identify_row(event.y)

            
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

app = ctk.CTk()

app.title("CTk - Tabviews")
app.geometry("1200x800")

# **Create a main container frame**
main_container = ctk.CTkFrame(app)
main_container.pack(fill="both", expand=True)  # Fills entire window

# **Create frame for header**
header_frame = ctk.CTkFrame(main_container, corner_radius=5)
header_frame.pack( side="top",fill="x", padx=10)
# **Load logo image**
logo_image = ctk.CTkImage(Image.open("asset/logo.png"), size=(80, 80))
# **Create label for app name with larger font**
app_name_label = ctk.CTkLabel(header_frame, text="FORENTO Fly Detector", font=("Arial", 20), anchor="center")
# **Pack logo and app name label in header**
logo_label = ctk.CTkLabel(header_frame, image=logo_image, text=" ", anchor='center')
logo_label.pack(side="left", padx=40, pady=5)
app_name_label.pack(side="left", pady=5)

# **Create frame for footer**
footer_frame = ctk.CTkFrame(main_container)
footer_frame.pack(side="bottom", fill="x", padx=5, pady=5, anchor="center")
# **Add copyright text with white color and centered alignment**
copyright_text = ctk.CTkLabel(footer_frame, text="© 2024 YOTTA", text_color="gray", anchor="center",)
copyright_text.pack(padx=10, pady=10, fill="x")

# Create tavview
my_tab = ctk.CTkTabview(main_container,
                        width= 1180,
                        height= 600,
                        border_width=1,
                        border_color="#1b1c1c",
                        corner_radius=14)
my_tab.pack(pady=10)

# Create tabs
auth = my_tab.add("Login")
detection = my_tab.add("Detection")
case_manager = my_tab.add("Case Manager")
user_manager = my_tab.add("User Manager")

# **Login form
auth_frame = ctk.CTkFrame(auth, 
                        border_width=1,
                        border_color="#101c12",
                        corner_radius=14)
auth_frame.pack(padx=250, pady=20, fill="both", expand=True)

label = ctk.CTkLabel(master=auth_frame, text= "Login to Forento App", font=("Roboto", 24))
label.pack(pady=40, padx=10)

login_entry = ctk.CTkEntry(master= auth_frame, placeholder_text="exemple@outlook.com")
login_entry.pack(pady=12, padx=10)
pwd_entry = ctk.CTkEntry(master= auth_frame, placeholder_text="password", show="*")
pwd_entry.pack(pady=12, padx=10)


login_btn = ctk.CTkButton(master = auth_frame, text="Login", command=login)
login_btn.pack(pady=12, padx=10)

# **Create frame for image display**
image_frame = ctk.CTkFrame(detection)
image_frame.pack(side="left", fill="both", expand=True, padx=5, pady=10)

# **Create a frame to group sidebar and image frame**
content_frame = ctk.CTkFrame(detection)
content_frame.pack(side="top", fill="both", expand=True, padx=5, pady=10)

# **Create frame for sidebar**
sidebar_frame = ctk.CTkFrame(content_frame, width=350, corner_radius=5)
sidebar_frame.pack(side="left", fill="y", padx=5, pady=5)

# **Create buttons in sidebar **
start_button = ctk.CTkButton(sidebar_frame, text="Start", command=lambda: start_detection())
start_button.pack(pady=10, padx=10, fill="x")

stop_button = ctk.CTkButton(sidebar_frame, text="Stop", command=lambda: stop_detection(), state="disabled")
stop_button.pack(pady=10, padx=10, fill="x")

open_folder_button = ctk.CTkButton(sidebar_frame, text="Open Folder", command=lambda: open_save_folder(), state="disabled")
open_folder_button.pack(pady=10, padx=10, fill="x")

exit_button = ctk.CTkButton(sidebar_frame, text="Exit", command=ask_question, state="normal")
exit_button.pack(pady=10, padx=10, fill="x")

# **Create label to display image (initially empty)
image_label = ctk.CTkLabel(image_frame, text="")
image_label.pack(fill="both", expand=True)

# **Create a label for confidence threshold spinbox**
confidence_label = ctk.CTkLabel(sidebar_frame, text="Confidence Threshold:")
confidence_label.pack(pady=10)

# **Create a spinbox for confidence threshold with initial value and increments**
confidence_var = ctk.IntVar(value=85)  # Initial value as 85 (represents 0.85)
confidence_entry = ctk.CTkEntry(
    sidebar_frame,
    width=150,
    textvariable=confidence_var
)
confidence_entry.pack(pady=10, padx=10)
# **Load play and pause icon images**
play_icon = ctk.CTkImage(Image.open("asset/play.png"), size=(20, 20))
pause_icon = ctk.CTkImage(Image.open("asset/pause.png"), size=(20, 20))

# **Create buttons for pause/play confidence threshold functionality (replace with your logic)**
pause_button = ctk.CTkButton(sidebar_frame, image= pause_icon, text=' ', corner_radius=100, command=lambda: pause_detection(), state="disabled")
pause_button.pack(pady=10, padx=10)

play_button = ctk.CTkButton(sidebar_frame, image= play_icon, text=' ', corner_radius=100, command=lambda: resume_detection(), state="disabled")
play_button.pack(pady=10, padx=10)

# **Create Table view for case manager
tableview = ctk.CTkFrame(master=case_manager)
tableview.pack(pady=10, padx=10, fill="both")
# Scrollbar
treeScroll = ttk.Scrollbar(tableview)
treeScroll.pack(side="right", fill="y")

value = [["Select","Case_ID","BSS N°","DEP N°","Chargés d'affaire","Saved Detections"]]

table = CTkTable(master=tableview, row=5, column=5, values=value)
table.pack(expand=True, fill="both", padx=20, pady=10)

# **Create frame for btns to manage the data in the table
manage_btn_frame = ctk.CTkFrame(case_manager)
manage_btn_frame.pack(pady=10, padx=10)

# **Create btns to manage the data in the table
add_case_btn = ctk.CTkButton(manage_btn_frame,
                            width=20,
                            height=10,
                            corner_radius=5,
                            text="+",
                            font=("Roboto",20)                          
                            )
add_case_btn.pack(expand=True, fill="both", padx=10, pady=10, side=LEFT)
rmv_case_btn = ctk.CTkButton(manage_btn_frame,
                            width=20,
                            height=10,
                            corner_radius=5,
                            text="-",
                            font=("Roboto",20),
                            state="disable"                             
                            )
rmv_case_btn.pack(expand=True, fill="both", padx=10, pady=10, side=LEFT)
modify_case_btn = ctk.CTkButton(manage_btn_frame,
                            width=20,
                            height=10,
                            corner_radius=5,
                            text="modify",
                            state="disable"                             
                            )
modify_case_btn.pack(expand=True, fill="both", padx=10, pady=10, side=LEFT)
save_case_btn = ctk.CTkButton(manage_btn_frame,
                            width=20,
                            height=10,
                            corner_radius=5,
                            text="save",
                            state="disable"                             
                            )
save_case_btn.pack(expand=True, fill="both", padx=10, pady=10, side=LEFT)
def add_case():
    
    return


def start_detection():
    global cap, running, save_directory, client
    
    # Check if an external camera is available
    cap = check_external_camera()
    if not cap:
        return

    # Check save directory only on initial start
    if not save_directory:
        save_directory = get_save_directory()
        if not save_directory:
            return  # Exit function if user cancels save directory selection
        else:
            print(f"Using save directory: {save_directory}")
    
    running = True
    start_button.configure(state="disabled")
    stop_button.configure(state="normal")
    open_folder_button.configure(state="normal")
    pause_button.configure(state="normal")  # Enable pause button when detection starts
    confidence_entry.configure(state="disabled")  # Disable confidence entry editing
    exit_button.configure(state="disabled") # Disable exit button when detection starts
    
    # detect_objects()  # Pass the collection object

def stop_detection():
    global running
    running = False
    start_button.configure(state="normal")
    stop_button.configure(state="disabled")
    open_folder_button.configure(state="normal")
    pause_button.configure(state="disable")
    exit_button.configure(state="normal")
    clear_image_label()

def open_save_folder():
    if save_directory:
        os.startfile(save_directory)

def clear_image_label():
    image_label.configure(image=None)
    image_label.image = None

# Function to pause detection
def pause_detection():
    global running
    if running:
        running = False
        pause_button.configure(state="normal")
        play_button.configure(state="normal")
        confidence_entry.configure(state="normal")  # Enable editing the entry

# Function to resume detection
def resume_detection():
    global running
    if not running:
        confidence_threshold = float(confidence_entry.get()) / 100.0  # Get and validate threshold
        confidence_entry.configure(state="disabled")  # Disable editing the entry
        start_detection()  # Call start_detection to handle further logic

app.mainloop()

