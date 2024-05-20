import os
import re
import smtplib
import datetime
from email import encoders
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart

archive_dir = "../data/archive"

def send_email_report(archive_dir):
    """
    Sends an email report with an attachment.

    Args:
        archive_dir: The directory path where the zipped archives are stored.
    """

    # Email configuration
    sender_email = "imanebelaid@hotmail.com"
    receiver_emails = ["belaidimane@gmail.com", "bakirdaoud@yotta.dz", "raniabenzaid@yotta.dz"]
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

    server.send_message(msg, from_addr=sender_email, to_addrs=receiver_emails)

# Call the function with the archive directory path
send_email_report("../data/archive")
