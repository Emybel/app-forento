import os
import win32com.client as win32

emails = {
    'recipient_name': 'belaidimane@gmail.com',
}

# Constract Outlook app instance
olApp = win32.Dispatch('Outlook.Application')
olNS = olApp.GetNameSpace('MAPI')

#Construct the email item object
mailItem = olApp.CreateItem(0)
mailItem.Subject = "Daily Detection Report - [date]"
mailItem.BodyFormat = 1
mailItem.Body = f"""
Hi,

This is a daily email with an attached zip file containing detections made on [Date].

Please see the attached image for details.

Best regards,
Forento
"""
mailItem.Attachments.Add(os.path.join(os.getcwd(), 'detected-fly_18-03-24_09-43-30.png'))
mailItem.Display()

for email in emails:
    mailItem.To = emails[email]

