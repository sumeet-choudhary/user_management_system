from flask import Blueprint, request, make_response, jsonify
from flask_restful import Resource
from application import api
from dotenv import load_dotenv
from flask_jwt_extended import jwt_required, get_jwt_identity
from application.role.controller import (find_role_by_name, add_new_role, update_role, find_role_by_id, delete_role,
                                         get_all_company_roles)
from application.user.controller import find_user
from bson import ObjectId

load_dotenv()
role_blueprint = Blueprint("role_blueprint", __name__)


class AddRole(Resource):
    """This api is used to add new roles with specified permissions to those roles"""
    @jwt_required()
    def post(self):
        try:
            admin_email = get_jwt_identity()
            role_name = request.json.get("role_name", None)
            permissions = request.json.get("permissions", None)

            if role_name in [None, ""] or permissions in [None, ""]:
                return make_response(jsonify({"message": "Please provide all necessary information."}), 200)

            already_user = find_user(admin_email)

            all_values = {"role_name": role_name, "permissions": permissions, "company_id": already_user["company_id"]}

            if not already_user:
                return make_response(jsonify({"message": "User with provided email does not exist."}), 200)

            if already_user["role"]["role_name"] != "Admin":
                return make_response(jsonify({"message": "Only Admin can add new roles"}), 200)

            already_role = find_role_by_name(role_name)
            if already_role:
                return make_response(jsonify({"message": "Role with given name already exist"}), 200)

            if add_new_role(all_values):
                return make_response(jsonify({"message": "Role added successfully."}), 200)

            else:
                return make_response(jsonify({"message": "Error adding role"}), 500)

        except Exception as e:
            return make_response(jsonify({"error": str(e)}, 500))


class UpdateRole(Resource):
    """This api is used to update the role and permissions of that role"""
    @jwt_required()
    def put(self, id):
        try:
            admin_email = get_jwt_identity()
            role_new_name = request.json.get("role_name", None)
            permissions = request.json.get("permissions", None)

            if id in [None, ""] or permissions in [None, ""] or role_new_name in [None, ""]:
                return make_response(jsonify({"message": "Please provide all necessary information."}), 200)

            already_user = find_user(admin_email)
            if not already_user:
                return make_response(jsonify({"message": "User with provided email does not exist."}), 200)

            if already_user["role"]["role_name"] != "Admin":
                return make_response(jsonify({"message": "Only Admin can update roles"}), 200)

            already_role = find_role_by_id(ObjectId(id))
            if not already_role:
                return make_response(
                    jsonify({"message": "Old role id that you are trying to update does not exist."}), 200)

            if already_role["role_name"] == "Admin":
                return make_response(jsonify({"message": "Admin role can't be updated."}), 200)

            if already_user["company_id"] != already_role["company_id"]:
                return make_response(jsonify({"message": "You can only update your company roles."}), 200)

            all_values = {"role_name": role_new_name, "permissions": permissions}
            if update_role(ObjectId(id), all_values):
                return make_response(make_response({"message": "Role updated successfully"}), 200)

            else:
                return make_response(jsonify({"message": "Error updated role"}), 500)

        except Exception as e:
            return make_response(jsonify({"error": str(e)}), 500)


class DeleteRole(Resource):
    """This api is used to delete the role and permissions of that role"""
    @jwt_required()
    def delete(self, id):
        try:
            admin_email = get_jwt_identity()

            if id in [None, ""]:
                return make_response(jsonify({"message": "Please provide all necessary information."}), 200)

            already_user = find_user(admin_email)

            # User checks
            if not already_user:
                return make_response(jsonify({"message": "User with provided email does not exist."}), 200)

            if already_user["role"]["role_name"] != "Admin":
                return make_response(jsonify({"message": "Only Admin can update roles"}), 200)
            
            already_role = find_role_by_id(ObjectId(id))

            # Roles conditions
            if not already_role:
                return make_response(
                    jsonify({"message": "Old role id that you are trying to delete does not exist."}), 200)

            if already_role["role_name"] == "Admin":
                return make_response(jsonify({"message": "Admin role can't be deleted."}), 200)

            if already_user["company_id"] != already_role["company_id"]:
                return make_response(jsonify({"message": "You can only delete your company roles."}), 200)

            if delete_role(ObjectId(id)):
                return make_response(make_response({"message": "Role deleted successfully"}), 200)
            else:
                return make_response(jsonify({"message": "Error updated role"}), 200)

        except Exception as e:
            return make_response(jsonify({"error": str(e)}), 500)


class GetAllCompanyRoles(Resource):
    """This api is used to delete the role and permissions of that role"""
    @jwt_required()
    def get(self):
        try:
            admin_email = get_jwt_identity()

            already_user = find_user(admin_email)

            # User checks
            if not already_user:
                return make_response(jsonify({"message": "User with provided email does not exist."}), 500)

            if already_user["role"]["role_name"] != "Admin":
                return make_response(jsonify({"message": "Only Admin can view roles"}), 500)
            
            all_company_roles = get_all_company_roles(already_user['company_id'])

            return make_response(make_response({"roles": all_company_roles}), 200)

        except Exception as e:
            return make_response(jsonify({"error": str(e)}), 500)


api.add_resource(AddRole, "/role")
api.add_resource(UpdateRole, "/role/<string:id>")   # Pass role_id with the endpoint here
api.add_resource(DeleteRole, "/role/<string:id>")   # Pass role_id with the endpoint here
api.add_resource(GetAllCompanyRoles, "/roles")
