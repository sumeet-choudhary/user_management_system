from flask import make_response, jsonify
from application import mongo

"""" ROLE COLLECTIONS """


def find_role_by_name(name):
    try:
        result = mongo.db.role_collection.find_one({"role_name": name})
        return result
    except Exception as e:
        return make_response(jsonify({"error": str(e)}))


def update_role(id, all_values):
    print(id, all_values)
    try:
        result = mongo.db.role_collection.update_one({"_id": id}, {"$set": all_values})
        return result
    except Exception as e:
        return make_response(jsonify({"error": str(e)}))


def add_new_role(all_values):
    try:
        result = mongo.db.role_collection.insert_one(all_values)
        return result
    except Exception as e:
        return make_response(jsonify({"error": str(e)}))


def find_role_by_id(role_id):
    try:
        result = mongo.db.role_collection.find_one({"_id": role_id})
        return result
    except Exception as e:
        return make_response(jsonify({"error": str(e)}))


def delete_role(id):
    try:
        result = mongo.db.role_collection.delete_one({"_id": id})
        return result
    except Exception as e:
        return make_response(jsonify({"error": str(e)}))


def get_all_company_roles(company_id):
    try:
        result = mongo.db.role_collection.find({"$or": [{"company_id": company_id}, {"role_name": "Admin"}]}, {"_id": 0})
        return list(result)
    except Exception as e:
        return make_response(jsonify({"error": str(e)}))
