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
import customtkinter
from PIL import Image
from tkinter import ttk
from email import encoders
from ultralytics import YOLO
from util.createjson import *
from tkinter import filedialog
from pymongo import MongoClient
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from datetime import datetime, timedelta
from CTkMessagebox import CTkMessagebox
from email.mime.multipart import MIMEMultipart
# from collections import defaultdict
# from customtkinter import CTkMessagebox

client = MongoClient("localhost", 27017)
db = client.forento
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

# Set appearance mode
customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("green")

# Create main app window
app = customtkinter.CTk()
# app.iconbitmap("asset/logo.png") # **Set a bitmap icon for the app**

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
header_frame = customtkinter.CTkFrame(app, corner_radius=5)
header_frame.pack( side="top",fill="x", padx=10, pady=5)

# **Load logo image**
logo_image = customtkinter.CTkImage(Image.open("asset/logo.png"), size=(80, 80))

# **Create label for app name with larger font**
app_name_label = customtkinter.CTkLabel(header_frame, text="FORENTO Fly Detector", font=("Arial", 20), anchor="center")

# **Pack logo and app name label in header**
logo_label = customtkinter.CTkLabel(header_frame, image=logo_image, text=" ", anchor='center')
logo_label.pack(side="left", padx=40, pady=5)
app_name_label.pack(side="left", pady=5)

# Create a container for the custom tab bar
tab_bar_frame = customtkinter.CTkFrame(app)
tab_bar_frame.pack(side="top", fill="x")

# Center the tab bar frame
tab_bar_inner_frame = customtkinter.CTkFrame(tab_bar_frame)
tab_bar_inner_frame.pack(side="top")

# Define tab names
tab_names = ["Detection", "User Management", "Case Management"]

# Create a frame for each tab content
tab_frames = [customtkinter.CTkFrame(app) for _ in tab_names]

# Create buttons for each tab and center them
tab_buttons = []
for idx, name in enumerate(tab_names):
    tab_button = customtkinter.CTkButton(
        tab_bar_inner_frame, text=name, command=lambda i=idx: switch_tab(i),
        fg_color="gray30", corner_radius=0, border_width=0  # Initial style
    )
    tab_button.pack(side="left", padx=5, pady=5)
    tab_buttons.append(tab_button)

# Display the first tab by default and update styles
tab_frames[0].pack(fill="both", expand=True)
update_tab_styles(0)

# Display the first tab by default
tab_frames[0].pack(fill="both", expand=True)

# **Create a main container frame**
main_container = customtkinter.CTkFrame(tab_frames[0])
main_container.pack(fill="both", expand=True)  # Fills entire window

# **Create a frame to group sidebar and image frame**
content_frame = customtkinter.CTkFrame(main_container)
content_frame.pack(side="top", fill="both", expand=True, padx=5, pady=10)

# **Create frame for sidebar**
sidebar_frame = customtkinter.CTkFrame(content_frame, width=350, corner_radius=5)
sidebar_frame.pack(side="left", fill="y", padx=5, pady=5)

# **Create frame for image display**
image_frame = customtkinter.CTkFrame(content_frame)
image_frame.pack(side="left", fill="both", expand=True, padx=5, pady=10)

# **Create frame for footer**
footer_frame = customtkinter.CTkFrame(main_container)
footer_frame.pack(side="bottom", fill="x", padx=5, pady=5, anchor="center")

# **Create buttons in sidebar (replace with your functionality)**
start_button = customtkinter.CTkButton(sidebar_frame, text="Start", command=lambda: start_detection())
start_button.pack(pady=10, padx=10, fill="x")

stop_button = customtkinter.CTkButton(sidebar_frame, text="Stop", command=lambda: stop_detection(), state="disabled")
stop_button.pack(pady=10, padx=10, fill="x")

open_folder_button = customtkinter.CTkButton(sidebar_frame, text="Open Folder", command=lambda: open_save_folder(), state="disabled")
open_folder_button.pack(pady=10, padx=10, fill="x")

exit_button = customtkinter.CTkButton(sidebar_frame, text="Exit", command=ask_question, state="normal")
exit_button.pack(pady=10, padx=10, fill="x")

# Create label to display image (initially empty)
image_label = customtkinter.CTkLabel(image_frame, text="")
image_label.pack(fill="both", expand=True)

# **Create a label for confidence threshold spinbox**
confidence_label = customtkinter.CTkLabel(sidebar_frame, text="Confidence Threshold:")
confidence_label.pack(pady=10)

# **Create a spinbox for confidence threshold with initial value and increments**
confidence_var = customtkinter.IntVar(value=85)  # Initial value as 85 (represents 0.85)
confidence_entry = customtkinter.CTkEntry(
    sidebar_frame,
    width=150,
    textvariable=confidence_var
)
confidence_entry.pack(pady=10, padx=10)
# **Load play and pause icon images**
play_icon = customtkinter.CTkImage(Image.open("asset/play.png"), size=(20, 20))
pause_icon = customtkinter.CTkImage(Image.open("asset/pause.png"), size=(20, 20))

# **Create buttons for pause/play confidence threshold functionality (replace with your logic)**
pause_button = customtkinter.CTkButton(sidebar_frame, image= pause_icon, text=' ', corner_radius=100, command=lambda: pause_detection(), state="disabled")
pause_button.pack(pady=10, padx=10)

play_button = customtkinter.CTkButton(sidebar_frame, image= play_icon, text=' ', corner_radius=100, command=lambda: resume_detection(), state="disabled")
play_button.pack(pady=10, padx=10)

# Create a new button in the sidebar
send_email_button = customtkinter.CTkButton(sidebar_frame, text="Send Email", command=lambda: send_email_report(latest_zip_path), state="disabled")
send_email_button.pack(pady=10, padx=10, fill="x")


# **Add copyright text with white color and centered alignment**
copyright_text = customtkinter.CTkLabel(footer_frame, text="© 2024 YOTTA", text_color="gray", anchor="center",)
copyright_text.pack(padx=10, pady=10, fill="x")

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
    send_email_button.configure(state="normal")  # Enable the "Send Email" button
    detect_objects()  # Pass the collection object

def stop_detection():
    global running
    running = False
    start_button.configure(state="normal")
    stop_button.configure(state="disabled")
    open_folder_button.configure(state="normal")
    pause_button.configure(state="disable")
    exit_button.configure(state="normal")
    send_email_button.configure(state="disable")  # disable the "Send Email" button
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
        zip_filename = f"archive_{date.strftime('%Y%m%d')}.zip"
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
    photo = customtkinter.CTkImage(img, size=(860, 820))
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
    to_recipients = ["belaidimane@gmail.com"]
    # cc_recipients = ["recipient2@example.com", "recipient3@example.com"]
    subject = f"Daily Detection Report - {datetime.datetime.now().strftime('%m-%d-%Y')}"

    # Find the zip file for the current date
    current_date = datetime.datetime.now().date()
    zip_pattern = r"archive_(\d{8})\.zip"
    zip_filename = f"archive_{current_date.strftime('%Y%m%d')}.zip"
    zip_path = os.path.join(archive_dir, zip_filename)

    if os.path.exists(zip_path):
        body_text = f"""Hi,

        This is a daily email with relevant information about detections made on {current_date.strftime('%m-%d-%Y')}.
        Please see the attached zip archive for captured fly images.

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
    msg["To"] = to_recipients
    # msg["To"] = ", ".join(receiver_emails)  # Join the list of recipients with commas
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

    server.send_message(msg, from_addr=sender_email, to_addrs=to_recipients) # to_addrs = to_receivers if we add Cc recipients


def send_email_in_thread(archive_path):
    try:
        send_email_report(archive_path)
    except Exception as e:
        print(f"Error sending email report: {e}")

def clear_save_directory(archive_dir, days=30):
    """
    Clears the archive_dir by removing ZIP files older than the specified number of days.

    Args:
        archive_dir (str): The path to the archive directory.
        days (int): The number of days to keep the ZIP files (default is 30 days).
    """
    now = datetime.now()
    cutoff_date = now - datetime.timedelta(days=days)

    for file_name in os.listdir(archive_dir):
        file_path = os.path.join(archive_dir, file_name)
        if file_name.endswith(".zip"):
            # Remove the file extension before parsing the date
            date_part = file_name.split("_")[1].split(".")[0]
            try:
                file_date = datetime.strptime(file_name.split("_")[1], "%Y%m%d").date()
                if file_date < cutoff_date:
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
    clear_save_directory(archive_path, days=30)

def run_scheduled_tasks():
    schedule.run_pending()
    app.after(60000, run_scheduled_tasks)  # Check for scheduled tasks every minute

# Schedule the archive_and_clear function to run at 23:59 (11:59 PM) every day
schedule.every().day.at("10:22").do(archive_and_clear)

# Bind the on_closing function to the window's closing event
app.protocol("WM_DELETE_WINDOW", ask_question)

# Run the scheduled tasks loop within the main application loop
run_scheduled_tasks()

app.mainloop()

# Release the capture when the app is closed
if cap:
    cap.release()
cv.destroyAllWindows()

