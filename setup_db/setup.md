** 1- Setup db **
1.1- Install mongodb.
1.2- Create a new database called "forento".
1.3- Create a new collections called: "users", "fly_detections".
1.4- Create a new index for the "fly_detections" collection with the following fields 
- "fly_id"
- "date"
- "detections" array to store all the day's detections.


If you plan to use authentication for your MongoDB database, you'll need to create a user with appropriate roles and ensure your application connects to the database using this user's credentials. Here are the steps and scripts required to set up MongoDB authentication:

### Step-by-Step Guide for Enabling Authentication in MongoDB

#### 1. **Enable Authentication in MongoDB Configuration**

1. **Locate the MongoDB Configuration File**:
   - On Linux, it’s typically located at `/etc/mongod.conf`.
   - On Windows, it might be located at `C:\Program Files\MongoDB\Server\{version}\bin\mongod.cfg`.

2. **Edit the Configuration File**:
   - Add or update the following lines to enable authorization:
     ```yaml
     security:
       authorization: "enabled"
     ```

3. **Restart MongoDB Service**:
   - Restart MongoDB to apply the changes.
     - On Windows:
       
        - Open Services:

           - Press Win + R to open the Run dialog.
            Type services.msc and press Enter. This opens the Services window.
            Locate MongoDB Service:

           - Scroll down or use the search bar to find the MongoDB service. It typically starts with "MongoDB" followed by the version number.
            Restart MongoDB:

           - Right-click on the MongoDB service.
            Select Restart from the context menu. This will stop and then start the MongoDB service with the new configuration.


#### 2. **Create Admin User**

1. **Start the MongoDB Shell**:
   ```bash
   mongo
   ```

2. **Switch to the `admin` Database**:
   ```javascript
   use admin
   ```

3. **Create an Admin User**:
   ```javascript
   db.createUser({
    user: "DevUser",
    pwd: "Dev_YOtt@",
    roles: [ { role: "userAdminAnyDatabase", db: "admin" }, "readWriteAnyDatabase", "dbAdmin", "userAdmin" ]
    })
   ```

#### 3. **Create Application User**

1. **Start the MongoDB Shell** with Admin Authentication:
   ```bash
   mongosh 
   Current Mongosh Log ID: 668aa4f51a0900421746b798
    Connecting to:          mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.2.5
    Using MongoDB:          7.0.9
    Using Mongosh:          2.2.5

    For mongosh info see: https://docs.mongodb.com/mongodb-shell/

    test> use admin
    switched to db admin
    admin> db.auth("DevUser", "Dev_YOtt@")
    { ok: 1 }
   ```

2. **Switch to Your Application Database**:
   ```javascript
   use forento
   ```

3. **Create an Application User**:
   ```javascript
   db.createUser({
     user: "Admin",
     pwd: "ForentoAdmin1055",
     roles: [
      { role: 'userAdmin', db: 'forento' },
      { role: 'dbAdmin', db: 'forento' },
      { role: 'readWrite', db: 'forento' }
    ]
   })
   ```

#### 4. **Setup the db**

run the `setup_db.py` script 


### Summary of Additional Steps

1. **Enable Authentication in MongoDB**:
   - Edit the MongoDB configuration file to enable authentication.
   - Restart the MongoDB service.

2. **Create Admin and Application Users**:
   - Use the MongoDB shell to create an admin user and an application-specific user.

3. **Update the Python Setup Script**:
   - Modify the script to connect to MongoDB with the application's user credentials.

4. **Provide Instructions for Users**:
   - Ensure users know how to install MongoDB, edit the configuration file, and run the setup script.

By following these steps, you can set up MongoDB with authentication, ensuring that your database is secure and that only authorized users can access it.

### ______________________________________________________________________________________

### Step-by-Step Guide to Creating Roles and Assigning Them to Users

1. **Define Your Roles:**
   - Before creating roles, decide on the different levels of access or functionality your application will need. Common roles might include `admin`, `user`, `manager`, `guest`, etc.

2. **Create a Roles Collection:**
   - You can create a collection named `roles` in your MongoDB database (`forento` in your case) to store role definitions. Each document in this collection represents a role with its specific permissions.

   Example schema for a role document:
   ```json
   {
       "_id": ObjectId("..."),
       "roleName": "admin",
       "permissions": [
           { "resource": "users", "actions": ["read", "write"] },
           { "resource": "detections", "actions": ["read"] }
           // Define more permissions as needed
       ]
   }
   ```
   Here, `permissions` can list resources (e.g., collections) and actions (e.g., `read`, `write`, `update`, `delete`) allowed for each role.

3. **Insert Roles into the Collection:**
   - Use MongoDB operations (either directly through a MongoDB client or programmatically using a script) to insert role documents into the `roles` collection.

   Example using Python and pymongo:
   ```python
   from pymongo import MongoClient

   client = MongoClient('mongodb://localhost:27017/')
   db = client['forento']

   roles_collection = db['roles']

   roles = [
       {
           "roleName": "admin",
           "permissions": [
               { "resource": "users", "actions": ["read", "write"] },
               { "resource": "detections", "actions": ["read"] }
           ]
       },
       {
           "roleName": "user",
           "permissions": [
               { "resource": "detections", "actions": ["read", "write"] }
           ]
       }
       // Add more roles as needed
   ]

   roles_collection.insert_many(roles)
   ```

4. **Grant Roles to Users:**
   - Once roles are defined, you can assign them to users during user creation or update operations.

   Example of granting a role to a user using pymongo:
   ```python
   def grant_role_to_user(username, role_name):
       db.command({
           "grantRolesToUser": username,
           "roles": [{"role": role_name, "db": "forento"}],
       })

   grant_role_to_user("username123", "admin")
   ```

5. **Handle Role-Based Access Control (RBAC):**
   - Implement logic in your application to check a user's role before allowing access to specific resources or performing actions. This can be done in your application's middleware or directly in API endpoints.

   Example in Python (using Flask):
   ```python
   from flask import request, abort

   def check_permission(role, resource, action):
       # Implement logic to check if 'role' has permission to perform 'action' on 'resource'
       return True  # Return True if allowed, False if not

   @app.route('/detections', methods=['GET'])
   def get_detections():
       user_role = get_user_role(request.headers.get('Authorization'))
       if check_permission(user_role, 'detections', 'read'):
           return jsonify({"detections": [...]})
       else:
           abort(403)  # Forbidden

   def get_user_role(auth_header):
       # Implement logic to retrieve user role from authentication token/header
       return "admin"  # Placeholder, actual implementation depends on your auth mechanism
   ```

6. **Testing and Validation:**
   - Test your role-based access control thoroughly to ensure that users can only access resources and perform actions allowed by their roles. Test edge cases and ensure proper error handling for unauthorized access attempts.

7. **Documentation and Maintenance:**
   - Document your roles, their permissions, and how they are assigned. Maintain your roles collection as your application evolves, adding or modifying roles as necessary.

### Best Practices

- **Least Privilege Principle:** Assign the minimum necessary permissions to each role to reduce the risk of unauthorized access.
- **Regular Review:** Periodically review and audit roles and their permissions to ensure they align with your application's security requirements.
- **Secure Authentication:** Use secure authentication mechanisms (like SCRAM-SHA-256) and manage credentials securely.

By following these steps and best practices, you can effectively implement role-based access control in your MongoDB-backed application. Adjust the specifics based on your application's requirements and architecture.