import os
import PIL
import sys
import cv2 as cv
import tkinter as tk
from tkinter import ttk
from tkinter import *
from CTkTable import *
import customtkinter as ctk
from PIL import Image, ImageTk
from CTkMessagebox import CTkMessagebox

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


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

app = ctk.CTk()

app.title("CTk - Tabviews")
app.geometry("1200x800")

value = [[1,2,3,4,5],
         [1,2,3,4,5],
         [1,2,3,4,5],
         [1,2,3,4,5],
         [1,2,3,4,5]]

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

# **Create buttons in sidebar (replace with your functionality)**
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

table = CTkTable(master=tableview, row=5, column=5, values=value)
table.pack(expand=True, fill="both", padx=20, pady=10)



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

