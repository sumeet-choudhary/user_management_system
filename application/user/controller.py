from flask import make_response, jsonify
from application import mongo
from application.role.controller import find_role_by_id


"""USER COLLECTION"""


def find_user(email):
    try:
        result = mongo.db.user_collection.find_one({"email": email})
        if result:
            role_id = result.get("role")
            if role_id:
                role = find_role_by_id(role_id)

                if role:
                    role["_id"] = str(role["_id"])  # Converting into string
                else:
                    role = {
                        "role_name": "",
                        "permissions": []
                    }    
                
                result["role"] = role  # Replace the role ID with the role details

        return result
    except Exception as e:
        return make_response(jsonify({"error": str(e)}))


def update_verification(email):
    try:
        result = mongo.db.user_collection.update_one({"email": email}, {"$set": {"verified": True}})
        return result
    except Exception as e:
        return make_response(jsonify({"error": str(e)}))


def add_new_user(all_values):
    try:
        result = mongo.db.user_collection.insert_one(all_values)
        return result
    except Exception as e:
        return make_response(jsonify({"error": str(e)}))


def set_password(email, password):
    try:
        result = mongo.db.user_collection.update_one({"email": email}, {"$set": {"password": password}})
        return result
    except Exception as e:
        return make_response(jsonify({"error": str(e)}))

