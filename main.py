import os
import sys
import json
import copy
import uuid
import shutil 
import random
import zipfile
import hashlib 
import datetime
import winsound
import cv2 as cv
import numpy as np
import ultralytics
import customtkinter
from PIL import Image
from ultralytics import YOLO
from util.createjson import *
from tkinter import filedialog
from pymongo import MongoClient
from CTkMessagebox import CTkMessagebox
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
secure_path = "/data/storage"

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
        return folder_path
    else:
        return None

def secure_folder(folder_path):
    """
    Attempts to set restrictive permissions on the specified folder using the 'chmod' command.

    Args:
        folder_path (str): The path to the folder you want to secure.

    Returns:
        bool: True if the command execution was successful, False otherwise.
    """
    try:
        # Set permissions to owner (you) having full access (read, write, execute)
        # Group and others have no access (no read, write, or execute)
        command = f"chmod 700 {folder_path}"
        os.system(command)
        return True
    except Exception as e:
        print(f"Error setting folder permissions: {e}")
        return False
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

# **Create a main container frame**
main_container = customtkinter.CTkFrame(app)
main_container.pack(fill="both", expand=True)  # Fills entire window

# **Create frame for header**
header_frame = customtkinter.CTkFrame(main_container, corner_radius=5)
header_frame.pack( side="top",fill="x", padx=10, pady=5)

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

# **Load logo image**
logo_image = customtkinter.CTkImage(Image.open("asset/logo.png"), size=(80, 80))

# **Create label for app name with larger font**
app_name_label = customtkinter.CTkLabel(header_frame, text="FORENTO Fly Detector", font=("Arial", 20), anchor="center")

# **Pack logo and app name label in header**
logo_label = customtkinter.CTkLabel(header_frame, image=logo_image, text=" ", anchor='center')
logo_label.pack(side="left", padx=40, pady=5)
app_name_label.pack(side="left", pady=5)

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

# **Add copyright text with white color and centered alignment**
copyright_text = customtkinter.CTkLabel(footer_frame, text="© 2024 YOTTA", text_color="gray", anchor="center",)
copyright_text.pack(padx=10, pady=10, fill="x")

def start_detection():
    global cap, running, save_directory, client
    
    # Create a new collection in mongodb to save the fly data
    # collection_name = new_collection(client,"forento", collection_prefix="detection-")
        
    # Check if an external camera is available
    cap = check_external_camera()
    if not cap:
        return

    # Check save directory only on initial start
    if not save_directory:
        save_directory = get_save_directory()
        if not save_directory:
            return  # Exit function if user cancels save directory selection

    running = True
    start_button.configure(state="disabled")
    stop_button.configure(state="normal")
    open_folder_button.configure(state="normal")
    pause_button.configure(state="normal")  # Enable pause button when detection starts
    confidence_entry.configure(state="disabled")  # Disable confidence entry editing
    exit_button.configure(state="disabled") # Disable exit button when detection starts
    
    detect_objects()  # Pass the collection object

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

def detect_objects():
    global running, cap, save_directory, collection_name
    
    now = datetime.datetime.now()
    date_str = now.strftime("%m-%d-%Y")
    time_str = now.strftime("%H:%M:%S")
    date_time_str = now.strftime("%m-%d-%y_%H-%M-%S")

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
    
    success = secure_folder(secure_path) # Secure the storage_path

    
    if success:
        print(f"Successfully secured folder: {secure_path}")
    else:
        print("Failed to secure folder. Check permissions or run with administrator privileges.")
    
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
                        
                        # now = datetime.datetime.now()
                        file_name = os.path.join(save_directory, f'detected-fly_{date_time_str}.png')
                        # Save the fly image using OpenCV or other libraries
                        cv.imwrite(secure_path, f'detected-fly_{date_time_str}.png')
                        # Generate unique identifier (hash of filename)
                        image_hash = hashlib.sha256(f'detected-fly_{date_time_str}.png'.encode()).hexdigest()
                        images_to_archive.append(file_name)
                        rgb_frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)  # Convert to RGB
                        pil_image = Image.fromarray(rgb_frame)  # Convert to PIL Image
                        winsound.Beep(3000, 500)
                        pil_image.save(file_name)
                        fly_info = [
                                {
                                    "time": time_str,  # Use the same variable containing the time string
                                    "confidence": rounded_confidence,
                                    "image_id": image_hash,  # Store image hash
                                    "image_path": f"{secure_path}/'detected-fly_{date_time_str}.png'",  # Store relative path
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

    # Archive fly images to ZIP file in ../data/archive dir

    # Update the GUI with the processed frame
    img = Image.fromarray(cv.cvtColor(frame, cv.COLOR_BGR2RGB))
    photo = customtkinter.CTkImage(img, size=(860, 820))
    image_label.configure(image=photo)
    image_label.image = photo

    # Schedule the next frame capture and detection
    if running:
        app.after(80, detect_objects)

# Bind the on_closing function to the window's closing event
app.protocol("WM_DELETE_WINDOW", ask_question)
app.mainloop()

# Release the capture when the app is closed
if cap:
    cap.release()
cv.destroyAllWindows()
