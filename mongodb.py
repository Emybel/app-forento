import os
import re
import sys
import copy
import psutil
import shutil
import random
import smtplib
import zipfile
import hashlib
import platform
import datetime
import schedule
import winsound
import threading 
import cv2 as cv
import collections
import numpy as np
import ultralytics
import tkinter as tk
import customtkinter as ctk
from helper import *
from PIL import Image
from tkinter import ttk
from email import encoders
from ultralytics import YOLO
from login import login_user
from functools import partial
from util.createjson import *
from tkinter import filedialog
from pymongo import MongoClient
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from CTkMessagebox import CTkMessagebox
from datetime import datetime, timedelta
from setup_db.roles import get_forento_roles
from email.mime.multipart import MIMEMultipart

client = MongoClient('mongodb://localhost:27017', username="Admin", password="ForentoAdmin1055", authSource="forento", authMechanism="SCRAM-SHA-256")
db = client["forento"]
collection = db['fly_detections']

# Define the path to the model
model_path = "forentoModel.pt"

# Define the classes
classes = ["fly", "larvae", "pupae"]

# Generate random colors for each class
def generate_random_colors(num_classes):
    """Generates a list of random BGR colors for a specified number of classes."""
    colors = []
    fly_class = [0, 206, 245]  # yellow color for fly
    colors.append(fly_class)
    larvae_class = [217, 22, 152]
    colors.append(larvae_class)
    pupae_class = [160, 199, 65]
    colors.append(pupae_class)  # Note: OpenCV uses BGR format
    return colors

detection_colors = generate_random_colors(len(classes))  # Generate colors once

# Load a pretrained YOLOv8n model
model = YOLO(model_path, 'v8')

# Initialize the camera (placeholder)
cap = None
# Global variables
running = False
save_directory = None
unique_fly_data = set()
filtered_data = []
images_to_archive = []
fly_data_per_frame = []
storage_path = "./data/storage"
archive_path = "./data/archive"
is_user_logged_in = False
login_window = None
app = None

now = datetime.now()
date_str = now.strftime("%m-%d-%Y")
time_str = now.strftime("%H:%M:%S")
date_time_str = now.strftime("%m-%d-%y_%H-%M-%S")

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
        return external_cameras[0]
    else:
        print("No external camera found")
        CTkMessagebox(title="No camera found", message="No external camera detected. Please ensure your camera is properly connected to your laptop.")
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
        
# Function to handle tab switching
def switch_tab(tab_index):
    for idx, frame in enumerate(tab_frames):
        if idx == tab_index:
            frame.pack(fill="both", expand=True)
        else:
            frame.pack_forget()
            
def update_tab_styles(selected_index):
    for idx, button in enumerate(tab_buttons):
        if idx == selected_index:
            button.configure(fg_color="medium sea green", font=("Arial", 12, "bold"), corner_radius=0, border_width=0)  # Active tab style
        else:
            button.configure(fg_color="transparent", font=("Arial", 12), corner_radius=0, border_width=0)  # Inactive tab style

def on_login_click(email_entry, pwd_entry, login_window):
    global is_user_logged_in, app
    email = email_entry.get()
    password = pwd_entry.get()
    logged_in_user_id, user_role, username = login_user(email, password)
    if logged_in_user_id and user_role:
        pwd_entry.delete(0, tk.END)
        email_entry.delete(0, tk.END)
        login_window.destroy()
        is_user_logged_in = True
        app.deiconify()  
        return logged_in_user_id, user_role, username
    else:
        CTkMessagebox(title="Login Failed", message="Invalid email or password")
        return None, None, None

def on_closing_login_window():
    global app
    if app:
        app.quit()  # Quit the main application loop
    # Ensure that the login window is destroyed properly
    if login_window:
        login_window.destroy()
    
def create_login_window():
    global login_window  # Declare login_window as global to access it in the closing function
    
    login_window = ctk.CTkToplevel()  # Create a new top-level window
    login_window.title("Forento Fly Detector | Login")
    login_window.geometry("480x900")

    header_frame = ctk.CTkFrame(login_window, corner_radius=5)
    header_frame.pack(side="top", fill="x", padx=10)

    logo_image = ctk.CTkImage(Image.open("asset/logo.png"), size=(80, 80))

    app_name_label = ctk.CTkLabel(header_frame, text="FORENTO Fly Detector", font=("Arial", 20), anchor="center")
    logo_label = ctk.CTkLabel(header_frame, image=logo_image, text=" ", anchor='center')
    logo_label.pack(side="left", padx=40, pady=5)
    app_name_label.pack(side="left", pady=5)

    login_frame = ctk.CTkFrame(login_window, corner_radius=5)
    login_frame.pack(padx=10, pady=10, fill="both", expand=True)

    auth_frame = ctk.CTkFrame(login_frame, border_width=1, border_color="#101c12", corner_radius=14)
    auth_frame.pack(padx=20, pady=20, fill="both", expand=True)

    label = ctk.CTkLabel(master=auth_frame, text="Login", font=("Roboto", 24))
    label.pack(pady=20, padx=10)

    email_entry = ctk.CTkEntry(master=auth_frame, placeholder_text="example@outlook.com")
    email_entry.pack(pady=12, padx=10)

    pwd_entry = ctk.CTkEntry(master=auth_frame, placeholder_text="Password", show="*")
    pwd_entry.pack(pady=12, padx=10)

    email = email_entry.get()
    password = pwd_entry.get()

    login_btn = ctk.CTkButton(
        master=auth_frame,
        text="Login",
        corner_radius=7,
        command=partial(on_login_click, email_entry, pwd_entry, login_window)
    )
    login_btn.pack(pady=15)

    # Set the protocol for the window close button
    login_window.protocol("WM_DELETE_WINDOW", on_closing_login_window)
    
    return login_window, email_entry, pwd_entry

def create_logout_icon(parent_frame, command):
    # Load the icon image
    logout_icon_image = ctk.CTkImage(Image.open("asset/logout.png"), size=(24, 24))  # Adjust the path and size as needed

    logout_icon_button = ctk.CTkButton(
                                parent_frame, 
                                image=logout_icon_image, 
                                text="", 
                                fg_color="gray30", 
                                corner_radius=24 // 2, 
                                width=24,
                                height=24)
    logout_icon_button.configure(command=command)
    logout_icon_button.pack(side="right", padx=10, pady=5)
    return logout_icon_button

def logout():
    global is_user_logged_in, app, login_window
    is_user_logged_in = False
    app.withdraw()
    login_window, email_entry, pwd_entry = create_login_window()
    login_window.mainloop()

# Set appearance mode
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("green")

# Create main app window
app = ctk.CTk()
# app.iconbitmap("asset/logo.png") # **Set a bitmap icon for the app**

app.withdraw()  # Hide the main app window initially

# Set height and width of the app
app_width = 1100
app_height = 850

# Get thes center of the screen
screen_width = app.winfo_screenwidth()
screen_height = app.winfo_screenheight()

# Get the position of the new top left position of the app
x =  (screen_width/2) - (app_width/2)
y =  (screen_height/2) - (app_height/2)
# Set window size
app.geometry(f"{app_width}x{app_height}+{int(x)}+{int(y)}")
app.resizable(height=False, width=False)
# Set window title
app.title("Forento Fly Detector")

# **Create frame for header**
header_frame = ctk.CTkFrame(app, corner_radius=5)
header_frame.pack( side="top",fill="x", padx=10, pady=5)

# **Load logo image**
logo_image = ctk.CTkImage(Image.open("asset/logo.png"), size=(80, 80))

# **Create label for app name with larger font**
app_name_label = ctk.CTkLabel(header_frame, text="FORENTO Fly Detector", font=("Arial", 20), anchor="center")

# **Pack logo and app name label in header**
logo_label = ctk.CTkLabel(header_frame, image=logo_image, text=" ", anchor='center')
logo_label.pack(side="left", padx=40, pady=5)
app_name_label.pack(side="left", pady=5)

# Create a container for the custom tab bar
tab_bar_frame = ctk.CTkFrame(app)
tab_bar_frame.pack(side="top", fill="x")

# logout_button = ctk.CTkButton(tab_bar_frame, text="Logout", command=logout)
# logout_button.pack(side="right", padx=5, pady=5)  # Position the button in the main app

# Add logout icon
create_logout_icon(tab_bar_frame, logout)

# Center the tab bar frame
tab_bar_inner_frame = ctk.CTkFrame(tab_bar_frame)
tab_bar_inner_frame.pack(side="top")

# Define tab names
tab_names = ["Detection", "User Management", "Case Management"]

# Create a frame for each tab content
tab_frames = [ctk.CTkFrame(app) for _ in tab_names]

# Create buttons for each tab and center them
tab_buttons = []
for idx, name in enumerate(tab_names):
    tab_button = ctk.CTkButton(
        tab_bar_inner_frame, text=name, command=lambda i=idx: switch_tab(i),
        fg_color="gray30", corner_radius=0, border_width=0  # Initial style
    )
    tab_button.pack(side="left", padx=5, pady=5)
    tab_buttons.append(tab_button)

# Function to switch between tabs
def switch_tab(tab_index):
    for frame in tab_frames:
        frame.pack_forget()
    tab_frames[tab_index].pack(fill="both", expand=True)
    update_tab_styles(tab_index)

# Function to update tab button styles
def update_tab_styles(active_tab_index):
    for idx, button in enumerate(tab_buttons):
        if idx == active_tab_index:
            button.configure(fg_color="green")
        else:
            button.configure(fg_color="transparent")

# Display the first tab by default and update styles
tab_frames[0].pack(fill="both", expand=True)
update_tab_styles(0)

# Display the first tab by default
tab_frames[0].pack(fill="both", expand=True)

# **Create a main container frame**
main_container = ctk.CTkFrame(tab_frames[0])
main_container.pack(fill="both", pady=2, expand=True)  # Fills entire window

# **Create a frame to group sidebar and image frame**
content_frame = ctk.CTkFrame(main_container)
content_frame.pack(side="top", fill="both", expand=True, padx=5, pady=10)

# **Create frame for sidebar**
sidebar_frame = ctk.CTkFrame(content_frame, width=350, corner_radius=5)
sidebar_frame.pack(side="left", fill="y", padx=5, pady=5)

# **Create frame for image display**
image_frame = ctk.CTkFrame(content_frame)
image_frame.pack(side="left", fill="both", expand=True, padx=5, pady=10)

# **Create frame for footer**
footer_frame = ctk.CTkFrame(app)
footer_frame.pack(side="bottom", fill="x", padx=5, pady=5, anchor="center")

# **Create buttons in sidebar (replace with your functionality)**
start_button = ctk.CTkButton(sidebar_frame, text="Start", command=lambda: start_detection())
start_button.pack(pady=10, padx=10, fill="x")

stop_button = ctk.CTkButton(sidebar_frame, text="Stop", command=lambda: stop_detection(), state="disabled")
stop_button.pack(pady=10, padx=10, fill="x")

open_folder_button = ctk.CTkButton(sidebar_frame, text="Open Folder", command=lambda: open_save_folder(), state="disabled")
open_folder_button.pack(pady=10, padx=10, fill="x")

exit_button = ctk.CTkButton(sidebar_frame, text="Exit", command=ask_question, state="normal")
exit_button.pack(pady=10, padx=10, fill="x")

# Create label to display image (initially empty)
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



"""
--------------------- DETECTION TAB FUNCTIONS ---------------------

"""
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
    # send_email_button.configure(state="normal")  # Enable the "Send Email" button
    detect_objects()  # Pass the collection object

def stop_detection():
    global running
    running = False
    start_button.configure(state="normal")
    stop_button.configure(state="disabled")
    open_folder_button.configure(state="normal")
    pause_button.configure(state="disable")
    exit_button.configure(state="normal")
    # send_email_button.configure(state="disable")  # disable the "Send Email" button
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

def archive_images(storage_path, archive_path):
    # Create the save_directory if it doesn't exist
    os.makedirs(archive_path, exist_ok=True)

    # Group files by creation date
    files_by_date = {}
    for file in os.listdir(storage_path):
        if file.endswith((".jpg", ".jpeg", ".png")):
            file_path = os.path.join(storage_path, file)
            file_name = os.path.basename(file_path)
            print(f'File name : {file_name}')
            date_str = file_name.split("_")[1]
            print(f'date part: {date_str}')
            try:
                creation_date = datetime.now().strptime(date_str, "%m-%d-%y").date()
                if creation_date not in files_by_date:
                    files_by_date[creation_date] = []
                files_by_date[creation_date].append(file_path)
            except ValueError:
                print(f"Skipping file {file_name} due to invalid date format")

    # Create a zip file for each date
    for date, files in files_by_date.items():
        zip_filename = f"detections_{date.strftime('%Y-%m-%d')}.zip"
        zip_path = os.path.join(storage_path, zip_filename)
        with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
            for file_path in files:
                archive.write(file_path, os.path.basename(file_path))
                print(f"Archiving {os.path.basename(file_path)} in {zip_filename}")
        
        # Move the ZIP file to the save_directory
        zip_src_path = os.path.join(storage_path, zip_filename)
        zip_dest_path = os.path.join(archive_path, zip_filename)
        shutil.move(zip_src_path, zip_dest_path)
        print(f"Moved {zip_filename} to {archive_path}")
def detect_objects():
    global running, cap, save_directory, collection_name
    
    if not running:
        return

    ret, frame = cap.read()

    # Check if frame capture was successful
    if not ret:
        print("Error: Unable to capture frame from camera")
        return
    
    # Get the confidence threshold from the entry, handle empty values
    try:
        confidence_threshold_str = confidence_entry.get()  # Get the text from the entry
        confidence_threshold = float(confidence_threshold_str) / 100.0  # Convert to float (0-1)
    except ValueError:
        confidence_threshold = 0.85  # Set default value if conversion fails

    # Predict on the frame
    detections = model.predict(source=frame, save=False, conf=confidence_threshold)
    detections = detections[0].numpy()
    
    if len(detections) != 0:

        if running:
            for detection in detections:
                boxes = detection.boxes

                for box in boxes:
                    # Retreive necessery data from the boxes
                    x_min, y_min, x_max, y_max = box.xyxy[0]  # Unpack the box information
                    class_id = int(box.cls[0])  # Assuming integer class IDs
                    conf = box.conf[0]  # The confidence of the prediction
                    rounded_confidence = str(round(conf * 100, 2))  # Convert confidence to string and round
                    color = detection_colors[class_id]  # Access color for the current class

                    # Draw rectangle and display class name and confidence
                    cv.rectangle(frame, (int(x_min), int(y_min)), (int(x_max), int(y_max)), color, 2)
                    font = cv.FONT_HERSHEY_COMPLEX
                    fontScale = 0.5  # Decrease the font size by 0.5
                    class_name = classes[class_id]  # Assuming classes is a dictionary mapping id to class name
                    text = class_name + " " + rounded_confidence + "%"
                    cv.putText(frame, text, (int(x_min), int(y_min) - 10), font, fontScale, (0, 0, 255), 1)

                    if detection.names[class_id] == "fly":
                        print("fly detected!")
                        
                        # Generate filenames with the global date_time_str
                        file_name = os.path.join(save_directory, f'detected-fly_{datetime.now().strftime("%m-%d-%y_%H-%M-%S")}.png')
                        file_name_storage = os.path.join(storage_path, f'detected-fly_{datetime.now().strftime("%m-%d-%y_%H-%M-%S")}.png')
                        
                        # Generate unique identifier (hash of filename)
                        image_hash = hashlib.sha256(f'detected-fly_{date_time_str}.png'.encode()).hexdigest()
                        images_to_archive.append(file_name)
                        rgb_frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)  # Convert to RGB
                        pil_image = Image.fromarray(rgb_frame)  # Convert to PIL Image
                        pil_image.save(file_name)
                        pil_image.save(file_name_storage)
                        winsound.Beep(3000, 500)
                        
                        fly_info = [
                                {
                                    "time": time_str,  # Use the same variable containing the time string
                                    "confidence": rounded_confidence,
                                    # "image_id": image_hash,  # Store image hash
                                    "image_path": f"{archive_path}/'detections_{date_str}.zip'",  # Store relative path
                                    "position": {
                                        "tl_x": round(float(x_min), 3),
                                        "tl_y": round(float(y_min), 3),
                                        "br_x": round(float(x_max), 3),
                                        "br_y": round(float(y_max), 3),
                                    }
                                }
                            ]                        
                        if fly_info:
                            query = {"date": date_str}  # Search for document with matching date
                            update = {"$push": {"detections": {"$each": fly_info}}}  # Update with new detections
                            result = collection.find_one_and_update(query, update, upsert=True)  # Upsert if not found

                            if result:
                                print(f"Updated detections for collection: {collection.name}")
                            else:
                                print(f"No document found for date: {date_time_str}. Creating new collection.")
                                # Consider creating a new document here if desired (optional)

    # Update the GUI with the processed frame
    img = Image.fromarray(cv.cvtColor(frame, cv.COLOR_BGR2RGB))
    photo = ctk.CTkImage(img, size=(860, 820))
    image_label.configure(image=photo)
    image_label.image = photo

    # Schedule the next frame capture and detection
    if running:
        app.after(80, detect_objects)

def send_email_report(archive_dir):
    """
    Sends an email report with an attachment.

    Args:
        archive_dir: The directory path where the zipped archives are stored.
    """

    # Email configuration
    sender_email = "imanebelaid@hotmail.com"
    receiver_emails = ["belaidimane@gmail.com"]
    # cc_recipients = ["recipient2@example.com", "recipient3@example.com"]
    subject = f"Daily Detection Report - {datetime.now().strftime('%m-%d-%Y')}"

    # Find the zip file for the current date
    current_date = datetime.now().date()
    zip_pattern = r"archive_(\d{8})\.zip"
    zip_filename = f"archive_{current_date.strftime('%Y%m%d')}.zip"
    zip_path = os.path.join(archive_dir, zip_filename)

    if os.path.exists(zip_path):
        body_text = f"""Hi,

        This is a daily email with relevant information about detections made on {current_date.strftime('%m-%d-%Y')}.
        
        Please see the attached zip file for captured fly images.

        Best regards,
        Forento
        """
    else:
        body_text = f"""Hi,

        This is a daily email with relevant information about detections made on {current_date.strftime('%m-%d-%Y')}.
        
        No flies were detected.

        Best regards,
        Forento
        """

    # Create message
    msg = MIMEMultipart()
    msg["From"] = sender_email
    # msg["To"] = to_recipients
    msg["To"] = ", ".join(receiver_emails)  # Join the list of recipients with commas
    msg["Subject"] = subject
    msg.attach(MIMEText(body_text, "plain"))

    # Attach the zip file if it exists
    if os.path.exists(zip_path):
        with open(zip_path, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f"attachment; filename={os.path.basename(zip_path)}",
        )
        msg.attach(part)

    app_pwd = "ipwtekmnicehktdm"
    server = smtplib.SMTP(host='smtp-mail.outlook.com', port=587)
    server.starttls()
    server.login(sender_email, app_pwd)

    status_code, response = server.ehlo()
    print(f"Echoing server : {status_code} {response}")

    server.send_message(msg, from_addr=sender_email, to_addrs=receiver_emails) # to_addrs = to_receivers if we add Cc recipients

def send_email_in_thread(archive_path):
    try:
        send_email_report(archive_path)
    except Exception as e:
        print(f"Error sending email report: {e}")

def clear_save_directory(archive_dir, days=365):
    """
    Clears the archive_dir by removing ZIP files older than the specified number of days.

    Args:
        archive_dir (str): The path to the archive directory.
        days (int): The number of days to keep the ZIP files (default is 30 days).
    """
    now = datetime.now()
    cutoff_date = now - timedelta(days=days)
    print(f"Cuatoff date: {cutoff_date.date()}")

    for file_name in os.listdir(archive_dir):
        file_path = os.path.join(archive_dir, file_name)
        if file_name.endswith(".zip"):
            # Remove the file extension before parsing the date
            date_part = file_name.split("_")[1].split(".")[0]
            print(f"date part: {date_part}")
            try:
                file_date = datetime.strptime(date_part, "%Y-%m-%d").date()
                print(f"File date: {file_date}")
                
                if file_date < cutoff_date.date():
                    os.remove(file_path)
                    print(f"Removed {file_path}")
            except Exception as e:
                print(f"Skipping file {file_name} due to invalid date format")
        print(f"Cleared {archive_dir} of ZIP files older than {days} days.")

def archive_and_clear():
    # Archive images
    archive_images(storage_path, archive_path)
    
    # Start a new thread for sending the email
    email_thread = threading.Thread(target=send_email_in_thread, args=(archive_path,))
    email_thread.start()

    # Clear the storage and save directories
    shutil.rmtree(storage_path)
    os.makedirs(storage_path)

    # Clear the archive_path of old ZIP files (e.g., older than 30 days)
    clear_save_directory(archive_path)

def run_scheduled_tasks():
    schedule.run_pending()
    app.after(60000, run_scheduled_tasks)  # Check for scheduled tasks every minute

# Schedule the archive_and_clear function to run at 23:59 (11:59 PM) every day
schedule.every().day.at("12:07").do(archive_and_clear)

"""
------------------------- CASE MANAGEMENT TAB FUNCTIONS ---------------------------
"""

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
    
    if check_email(new_email):
        CTkMessagebox(title="Email already exists", message="This email is already used by another user. Please give another email adress.")
        return

    try:
        update_user(current_email, username if username else None, new_email if new_email else None, selected_role if selected_role else None, pwd if pwd else None)
        CTkMessagebox(master=app, title="Success", message="User updated successfully!")
        # Clear the fields
        username_entry.delete(0, tk.END)
        pwd_entry.delete(0, tk.END)
        email_entry.delete(0, tk.END)
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

"""
------------------------- USER MANAGEMENT TAB FUNCTIONS ---------------------------

"""
# Create a frame for the main content of the Case Management tab
main_frame = ctk.CTkFrame(tab_frames[1])
main_frame.pack(padx=10, pady=10, fill="both", expand=True)

# Add a frame for the treeview
treeview_frame = ctk.CTkFrame(main_frame, corner_radius=5)
treeview_frame.pack(padx=10, pady=10, fill="both", expand=True)

# Add a treeview to display users
columns = ("Username", "Email", "Role")
user_treeview = ttk.Treeview(treeview_frame, columns=columns, show="headings", height=18)
for col in columns:
    user_treeview.heading(col, text=col)
    user_treeview.column(col, minwidth=100, width=150, stretch=tk.NO)

user_treeview.pack(padx=10, pady=10, fill="both", expand=True)
scrollbar = ttk.Scrollbar(user_treeview, orient="vertical", command=user_treeview.yview)
user_treeview.configure(yscroll=scrollbar.set)
scrollbar.pack(side="right", fill="y")

# Add form to manage users data
form_frame = ctk.CTkFrame(main_frame, corner_radius=5)
form_frame.pack(padx=5, pady=5, fill="both", expand=True)

auth_frame = ctk.CTkFrame(form_frame, border_width=1, border_color="#101c12", corner_radius=14)
auth_frame.pack(padx=5, pady=5, fill="both", expand= True)

sub_frame1 = ctk.CTkFrame(auth_frame, fg_color="transparent", width=100)
sub_frame2 = ctk.CTkFrame(auth_frame, fg_color="transparent", width= 100)

ctk.CTkLabel(auth_frame, text="Manage users", font=("Roboto", 24)).pack(side="top", padx=5, pady= 10)
sub_frame1.pack(padx=10, pady=5)
sub_frame2.pack(padx=10, pady=5)


ctk.CTkLabel(sub_frame1, text="Full name:").pack(side="left", padx=5, pady= 20)
username_entry = ctk.CTkEntry(sub_frame1, placeholder_text="Full name")
username_entry.pack(side="left", padx=5, pady= 5, fill="x", expand=True)

ctk.CTkLabel(sub_frame1, text="Password:").pack(side="left", padx=5, pady= 20)
pwd_entry = ctk.CTkEntry(sub_frame1, placeholder_text="Password", show="*")
pwd_entry.pack(side="left", padx=5, pady= 5, fill="x", expand=True)

ctk.CTkLabel(sub_frame2, text="Email:").pack(side="left", padx=5, pady= 20)
email_entry = ctk.CTkEntry(sub_frame2, placeholder_text="example@outlook.com")
email_entry.pack(side="left", padx=5, pady= 5, fill="x", expand=True)

ctk.CTkLabel(sub_frame2, text="Role:").pack(side="left", padx=5, pady= 20)
role_names = [role for role in roles]
roles_menu = ctk.CTkComboBox(sub_frame2, values=role_names)
roles_menu.pack(side="left", padx=5, pady= 5, fill="x", expand=True)

# Buttons Frame
button_frame = ctk.CTkFrame(auth_frame, fg_color="transparent")
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

"""
------------------------- CASE MANAGEMENT TAB FUNCTIONS ---------------------------
"""

def update_listbox(listbox, entries):
        """Update the listbox with new entries."""
        listbox.delete(0, tk.END)
        for entry in entries:
            listbox.insert(tk.END, entry["username"])
        
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

    if not bss_num.strip() or not dep_num.strip() or not status or not assigned_to.strip():
        CTkMessagebox(title="Missing Information", message="Please fill out all fields.")
        return

    try:
        create_case(bss_num, dep_num, status, assigned_to_id, technician_ids_list)
        CTkMessagebox(master=app, title="Success", message=f"Case '{bss_num}' created successfully!")
        bss_num_entry.delete(0, tk.END)
        dep_num_entry.delete(0, tk.END)
        refresh_case_list()
    except Exception as e:
        CTkMessagebox(master=app, title="Error Creating Case", message=f"Error Creating Case: {e}")
        print(f"Error Creating Case: {e}")

# Variables to store selected user IDs
assigned_to_id = None
technician_ids_list = []
def modify_selected_case():
    """Modifies the selected case's information in the database."""
    selected_item = case_treeview.selection()
    if not selected_item:
        CTkMessagebox(master=app, title="Error", message="Please select a case to modify.")
        return

    # Get the bss_num of the selected case
    selected_case = case_treeview.item(selected_item, "values")
    bss_num = selected_case[0]  # Assuming BSS Number is the first column

    # Retrieve and strip the values from the entries and dropdowns
    new_bss_num = bss_num_entry.get().strip()
    dep_num = dep_num_entry.get().strip()
    status = status_menu.get()
    assigned_to_username = assigned_to_dropdown.get().strip()

    # Check if at least one field is filled
    if not new_bss_num and not dep_num and not status and not assigned_to_id:
        CTkMessagebox(master=app, title="Missing Information", message="Please fill out at least one field.")
        return

    # Build the update_fields dictionary based on provided inputs
    update_fields = {}
    if new_bss_num:
        update_fields["bss_num"] = new_bss_num
    if dep_num:
        update_fields["dep_num"] = dep_num
    if status:
        update_fields["status"] = status
    if assigned_to_username:
        try:
            # Fetch the ObjectId for the assigned_to username
            assigned_to_id = get_user_id_by_username(assigned_to_username)
            if assigned_to_id:
                update_fields["assigned_to"] = ObjectId(assigned_to_id)
            else:
                CTkMessagebox(master=app, title="Error", message="Invalid assigned to username.")
                return
        except Exception as e:
            CTkMessagebox(master=app, title="Error", message=f"Error fetching user ID: {e}")
            print(f"Error fetching user ID: {e}")
            return

    # Include technician_ids if they are provided
    if technician_ids_list:
        update_fields["technician_ids"] = [ObjectId(tech_id) for tech_id in technician_ids_list]

    try:
        update_case(bss_num, update_fields)
        CTkMessagebox(master=app, title="Success", message="Case updated successfully!")
        bss_num_entry.delete(0, tk.END)
        dep_num_entry.delete(0, tk.END)
        refresh_case_list()
    except Exception as e:
        CTkMessagebox(master=app, title="Error", message=f"Error Updating Case: {e}")
        print(f"Error Updating Case: {e}")

def get_user_id_by_username(username):
    """Fetches the user ID (ObjectId) for a given username."""
    user = db.users.find_one({"username": username})
    return str(user["_id"]) if user else None

def delete_selected_case():
    """Deletes the selected case from the database."""
    selected_item = case_treeview.selection()
    if not selected_item:
        CTkMessagebox(master=app, title="Error", message="Please select a case to delete.")
        return

    case_bss_num = case_treeview.item(selected_item, "values")[0]
    try:
        delete_case(case_bss_num)
        CTkMessagebox(master=app, title="Success", message="Case deleted successfully!")
        refresh_case_list()
    except Exception as e:
        CTkMessagebox(master=app, title="Error", message=f"Error Deleting Case: {e}")
        print(f"Error Deleting Case: {e}")

"""
---------------------- CASE MANAGEMENT TAB ----------------------

"""
cases = get_all_cases()
users = get_all_users()

# Create a frame for the main content of the Case Management tab
main_frame = ctk.CTkFrame(tab_frames[2])
main_frame.pack(padx=10, pady=10, fill="both", expand=True)

# Add a frame for the treeview
treeview_frame = ctk.CTkFrame(main_frame, corner_radius=5)
treeview_frame.pack(padx=10, pady=10, fill="both", expand=True)

# Treeview for Cases
columns = ("BSS Number", "Department Number", "Expert", "Technicians", "Status")

case_treeview = ttk.Treeview(treeview_frame, columns=columns, show="headings", height=5)
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

ctk.CTkLabel(form_frame, text="Manage cases", font=("Roboto", 24)).pack(side="top", padx=5, pady=10)

# Input Fields with Labels
input_frame = ctk.CTkFrame(form_frame, fg_color="transparent", width=200)
input_frame.pack(pady=10)

ctk.CTkLabel(input_frame, text="BSS Number:").pack(side="left", padx=5)
bss_num_entry = ctk.CTkEntry(input_frame, placeholder_text="BSS Number")
bss_num_entry.pack(side="left", padx=15)

ctk.CTkLabel(input_frame, text="Department Number:").pack(side="left", padx=5)
dep_num_entry = ctk.CTkEntry(input_frame, placeholder_text="Department Number")
dep_num_entry.pack(side="left", padx=15)

ctk.CTkLabel(input_frame, text="Status:").pack(side="left")
status_menu = ctk.CTkComboBox(input_frame, values=["open", "closed", "in_progress"])
status_menu.pack(side="left", padx=15)

# Assigned To and Technician IDs
list_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
list_frame.pack(padx=50, pady=10, fill="x")

sub_frame1 = ctk.CTkFrame(list_frame, fg_color="transparent", width=200)
sub_frame2 = ctk.CTkFrame(list_frame, fg_color="transparent", width=100)
sub_frame1.pack(side="left", padx=50, pady=5)
sub_frame2.pack(side="left", padx=10, pady=5)

ctk.CTkLabel(sub_frame1, text="Expert Assigned To:").pack(side="left", padx=5)

assigned_to_dropdown = ttk.Combobox(sub_frame1)
assigned_to_dropdown.pack(side=["left"], padx=10, fill="x")

# Populate dropdowns
assigned_to_dropdown['values'] = [entry["username"] for entry in get_usernames("Expert")]

ctk.CTkLabel(sub_frame2, text="Technician IDs:").pack(side="left", padx=5)

technician_ids_listbox = tk.Listbox(sub_frame2, selectmode=tk.MULTIPLE, width=80)
technician_ids_listbox.pack(side=["left"], pady=5, padx=5, fill="y")

# Populate listbox
technician_ids_listbox.insert(tk.END, *[entry["username"] for entry in get_usernames("Technician")])

# Buttons Frame
button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
button_frame.pack(pady=10)

create_btn = ctk.CTkButton(button_frame, text="Create Case", corner_radius=7, command=create_new_case)
modify_btn = ctk.CTkButton(button_frame, text="Modify Case", corner_radius=7, command=modify_selected_case)
delete_btn = ctk.CTkButton(button_frame, text="Delete Case", corner_radius=7, command=delete_selected_case)

create_btn.pack(side="left", padx=10)
modify_btn.pack(side="left", padx=10)
delete_btn.pack(side="left", padx=10)

# **Add copyright text with white color and centered alignment**
copyright_text = ctk.CTkLabel(footer_frame, text="© 2024 YOTTA", text_color="gray", anchor="center",)
copyright_text.pack(padx=10, pady=10, fill="x")



# Bind the on_closing function to the window's closing event
app.protocol("WM_DELETE_WINDOW", ask_question)

# Run the scheduled tasks loop within the main application loop
run_scheduled_tasks()

"""
--------------------- CASE MANAGEMENT TAB FUNCTIONS ---------------------
"""

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

# login window
login_window, email_entry, pwd_entry = create_login_window()

app.mainloop()

# Release the capture when the app is closed
if cap:
    cap.release()
cv.destroyAllWindows()

