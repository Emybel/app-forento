# from pymongo import MongoClient

# client = MongoClient("localhost", 27017)

# db = client.forento

# detection = db.flyDetectionData

# for data in detection.find():
#     print(data)

import os
import re
import shutil
import zipfile
from datetime import datetime

def archive_images(storage="./data/storage", save_directory="./data/archive"):
    # Create the save_directory if it doesn't exist
    os.makedirs(save_directory, exist_ok=True)

    # Group files by creation date
    files_by_date = {}
    for file in os.listdir(storage):
        if file.endswith((".jpg", ".jpeg", ".png")):
            file_path = os.path.join(storage, file)
            file_name = os.path.basename(file_path)
            print(f'File name : {file_name}')
            date_str = file_name.split("_")[1]
            print(f'date part:{date_str}')
            try:
                creation_date = datetime.strptime(date_str, "%m-%d-%y").date()
                if creation_date not in files_by_date:
                    files_by_date[creation_date] = []
                files_by_date[creation_date].append(file_path)
            except ValueError:
                print(f"Skipping file {file_name} due to invalid date format")

    # Create a zip file for each date
    for date, files in files_by_date.items():
        zip_filename = f"archive_{date.strftime('%Y%m%d')}.zip"
        zip_path = os.path.join(save_directory, zip_filename)
        with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
            for file_path in files:
                archive.write(file_path)
                print(f"Archiving {os.path.basename(file_path)} in {zip_filename}")

archive_images()