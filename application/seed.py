"""Created a function to add default admin role into database"""


def create_default_admin_role(mongo):
    admin_role = mongo.db.role_collection.find_one({"role_name": "Admin"})
    if not admin_role:
        # If the "Admin" role doesn't exist, create it with the necessary permissions
        all_values = {
            "role_name": "Admin",
            "permissions": ["Admin has all the access"]  # Add the required permissions here
        }
        mongo.db.role_collection.insert_one(all_values)
