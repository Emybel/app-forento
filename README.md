## Forento Fly Detector - Setting Up the Environment

This guide will help you set up the environment to contribute to the Forento Fly Detector project.

**Requirements:**

* Python (version 3.10 or higher)
* pip (package installer for Python)

**Steps:**

1. **Install Python:**
   - Download and install Python from the official website (https://www.python.org/downloads/). Make sure to add Python to your system path during installation.

2. **Create a virtual environment (recommended):**
   - Open a terminal or command prompt.
   - Run the following command to create a virtual environment named `venv`:

     ```bash
     python -m venv venv
     ```

   - Activate the virtual environment:

     ```bash
     # On Windows
     venv\Scripts\activate

     # On Linux/macOS
     source venv/bin/activate
     ```

3. **Clone the repository:**
   - Use Git to clone the Forento Fly Detector repository from GitHub. Replace `<username>` with your GitHub username and `<repository-name>` with the actual repository name:

     ```bash
     git clone [https://github.com/](https://github.com/)<username>/<repository-name>.git
     ```

4. **Install dependencies:**
   - Navigate to the cloned repository directory:

     ```bash
     cd <repository-name>
     ```

   - Install the required Python packages listed in the `requirements.txt` file using pip:

     ```bash
     pip install -r requirements.txt
     ```

**You're all set!**

- You can now run the application or start contributing to the development process.

**Additional Notes:**

- Consider using a version control system like Git to manage your code changes.
- Refer to the project documentation for further details on contributing guidelines and development practices.

**For Developers:**

This project uses a custom `util` directory containing helper functions for image processing, JSON handling, and fly data management. Familiarize yourself with the code in these files to understand the application's logic.

