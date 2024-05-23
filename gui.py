from tkinter import *
from tkinter import ttk  # for CTkTable
from tkinter import messagebox
import bcrypt
# Database connection (replace with your specific library and connection code)
import pymongo

# Connect to MongoDB (example)
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["your_database_name"]
users_collection = db["users"]


# Function to create the user form
def create_user_form(master):
    # Labels and entry fields for user information
    full_name_label = Label(master, text="Full Name:")
    full_name_label.pack()

    full_name_var = StringVar()
    full_name_entry = Entry(master, textvariable=full_name_var)
    full_name_entry.pack()
    
    email_label = Label(master, text="Email:")
    email_label.pack()

    email_var = StringVar()
    email_entry = Entry(master, textvariable=email_var, show="Enter Email Address")  # Placeholder text
    email_entry.pack()

    pwd_label = Label(master, text="Password:")
    pwd_label.pack()

    pwd_var = StringVar()
    pwd_entry = Entry(master, textvariable=pwd_var, show="*")  # Hide password with asterisks
    pwd_entry.pack()

    role_label = Label(master, text="Role:")
    role_label.pack()

    # Define string variable to store the selected role value
    role_var = StringVar()

    # Create radio buttons for each role option
    expert_radiobutton = Radiobutton(master, text="Expert", variable=role_var, value="Expert")
    technicien_radiobutton = Radiobutton(master, text="Technicien", variable=role_var, value="Technicien")
    technicien_radiobutton.pack()

    # Save button
    save_button = Button(master, text="Save User", command=lambda: save_user(
    full_name_var.get(),
    email_var.get(),
    pwd_var.get(),
    role_var.get()
    ))

    save_button.pack()

# Function to create the user table
def create_user_table(master):
    user_table = ttk.CTkTable(master, columns=("Full Name", "Email", "Role"))
    user_table.pack(fill=BOTH, expand=True)

    # Bind selection events for table rows
    user_table.bind("<ButtonRelease-1>", lambda event: select_user(event, user_table))

    # Load existing users from database (example)
    load_users(user_table)

    return user_table  # Note: return the user_table object

# Function to delete user frpom table
def delete_user(user_table):
    # Get selected row data
    selected_row = user_table.focus()
    if not selected_row:
        return  # No row selected, do nothing

    # Confirmation dialog (optional)
    confirmation = messagebox.askquestion("Confirm Delete", "Are you sure you want to delete this user?")
    if confirmation != "yes":
        return  # User cancelled deletion

    # Get email (or other unique identifier) from selected row
    selected_user = user_table.item(selected_row)["values"]
    email = selected_user[1]  # Assuming email is the second column

    # Delete user from database (example)
    users_collection.delete_one({"email": email})

    # Reload user table
    load_users(user_table)

def hash_password(password):
    """Hashes a password using bcrypt."""
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()  # Generate a random salt
    hashed_password = bcrypt.hashpw(password_bytes, salt)
    return hashed_password.decode("utf-8")

# Function to save a new user
def save_user(full_name_var, email_var, pwd_var, role_var, user_table):
    # Validate user information (optional)

    # Password hashing (highly recommended for security)
    hashed_password = hash_password(password)  # Replace with your password hashing function
    
    # Insert into users collection
    users_collection.insert_one({
        "full_name": full_name,
        "email": email,
        "password": hashed_password,  # Use hashed password
        "role": role
    })

    # Clear form entry fields
    full_name_var.set("")
    email_var.set("")
    pwd_var.set("")
    role_var.set("")  # Clear selected radio button

    # Reload user table
    load_users(user_table)


# Function to load users from the database
def load_users(user_table):
    # Clear existing table data
    user_table.delete(*user_table.get_children())

    # Get all users from database (example)
    users = users_collection.find({})

    # Add each user to the table
    for user in users:
        user_table.insert("", tk.END, values=(user["full_name"], user["email"], user["role"]))

# Function to handle user selection
def select_user(event, user_table):
    """
    Handles user selection in the user table and populates the form fields.

    Args:
        event: The event object triggered by the user selection.
        user_table: The CTkTable instance representing the user table.
    """

    # Get selected row data
    selected_row = user_table.focus()
    if not selected_row:
        return  # No row selected, do nothing

    selected_user = user_table.item(selected_row)["values"]

    # Get references to form entry field variables (assuming they are defined elsewhere)
    global full_name_var, email_var, pwd_var, role_var  # Assuming global variables

    # Populate form fields with selected user data
    full_name_var.set(selected_user[0])  # Assuming full name is the first column
    email_var.set(selected_user[1])  # Assuming email is the second column

    # Password field might not be editable (security concern)
    # pwd_var.set(selected_user[2])  # Assuming password is the third column (not recommended)

    # Set the selected role based on the value in the selected user data
    role_var.set(selected_user[2])  # Assuming role is the third column

    # Update save button text (optional)
    # save_button.config(text="Update User")  # Assuming a global save button


# Function to modify a user (can be added later)
# def modify_user():
#     # ... (implement logic to update user data in database and reload table)

# Main function to create the GUI
def main():
    master = Tk()
    master.title("User Manager")

    # Create two frames side-by-side
    form_frame = Frame(master, width=400, height=500, relief=RIDGE, bd=2)
    form_frame.pack(side=LEFT, fill=Y)

    user_table_frame = Frame(master, width=400, height=500, relief=RIDGE, bd=2)
    user_table_frame.pack(side=RIGHT, fill=Y)

    create_user_form(form_frame)
    create_user_table(user_table_frame)


    mainloop()


