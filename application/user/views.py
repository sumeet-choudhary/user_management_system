from flask import Blueprint, request, make_response, jsonify
from flask_restful import Resource
from application import api
from datetime import datetime, timedelta
import jwt
from dotenv import load_dotenv
import bcrypt
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from application.user.controller import add_new_user, find_user, update_verification, set_password
from application.role.controller import find_role_by_name
from application.celery_config.celery_task import send_mail
from bson import ObjectId
import uuid  # Universally Unique Identifier

load_dotenv()
user_blueprint = Blueprint("user_blueprint", __name__)


class UserRegister(Resource):
    """This api takes user inputs and if meets all conditions then register that user"""

    def post(self):
        try:
            name = request.json.get("name", None)
            email = request.json.get("email", None)
            company_name = request.json.get("company_name", None)
            admin_role_id = find_role_by_name("Admin")["_id"]
            verified = False

            if name in [None, ""] or email in [None, ""] or company_name in [None, ""]:
                return make_response(jsonify({"message": "Please provide all necessary information."}), 200)

            company_id = str(uuid.uuid4())

            all_values = {
                "name": name,
                "email": email,
                "company_name": company_name,
                "role": admin_role_id,
                "company_id": company_id,
                "verified": verified
            }

            already_user = find_user(email)
            if already_user:
                return make_response(jsonify({"message": "This user already exist"}), 200)

            expire_token_time = datetime.now() + timedelta(minutes=15)
            expire_epoch_time = int(expire_token_time.timestamp())
            made_payload = {"email": email, "exp": expire_epoch_time}
            # jwt token to pass in verify mail
            made_verification_token = jwt.encode(made_payload, "sumeet", algorithm="HS256")

            if add_new_user(all_values):
                send_mail.delay(email, made_verification_token)
                return make_response(jsonify({"message": "User registered successfully. A mail has been sent to "
                                                         "your email for verification."}), 200)
            else:
                return make_response(jsonify({"message": "Error registering user"}), 200)

        except Exception as e:
            return make_response(jsonify({"error": str(e)}, 500))


class UserVerify(Resource):
    """This api is used to verify the user on their provided email"""

    def get(self):
        try:
            token = request.args.get("token")
            if token:
                token_decoded = jwt.decode(token, "sumeet", algorithms=["HS256"])
                email = token_decoded["email"]

                already_user = find_user(email)
                if not already_user:
                    return make_response(jsonify({"message": "User with provided email does not exist."}), 200)
                else:
                    update_verification(email)
                    return make_response(jsonify({"message": "Your account is now verified!"}), 200)

        except Exception as e:
            return make_response(jsonify({"message": str(e)}), 500)


class UserSetPassword(Resource):
    """This api is used to set user password before logging in"""

    def post(self):
        try:
            email = request.json.get("email", None)
            password = request.json.get("password", None)

            if email in [None, ""] or password in [None, ""]:
                return make_response(jsonify({"message": "Please provide all necessary information."}), 200)

            password = password.encode()
            hash_password = bcrypt.hashpw(password, bcrypt.gensalt(8))

            already_user = find_user(email)
            if not already_user:
                return make_response(jsonify({"message": "User with provided email does not exist."}), 200)

            verified = already_user["verified"]
            if not verified:
                return make_response(jsonify({"message": "Please verify your email first"}), 200)

            set_password(email, hash_password)
            return make_response(jsonify({"message": "Password set successfully!"}), 200)

        except Exception as e:
            return make_response(jsonify({"message": str(e)}), 500)


class UserLogin(Resource):
    """This api is used to login the user with email and password"""

    def post(self):
        try:
            email = request.json.get("email", None)
            password = request.json.get("password", None)

            if email in [None, ""] or password in [None, ""]:
                return make_response(jsonify({"message": "Please provide all necessary information."}), 200)

            password = password.encode()

            already_user = find_user(email)
            if not already_user:
                return make_response(jsonify({"message": "User with provided email does not exist."}), 200)

            verified = already_user["verified"]
            if not verified:
                return make_response(jsonify({"message": "Please verify your email first"}), 200)

            if "password" not in already_user:
                return make_response(jsonify({"message": "First set your password before trying to login"}), 200)

            if bcrypt.checkpw(password, already_user["password"]) is False:
                return make_response(jsonify({"message": "Wrong Password"}))

            access_token = create_access_token(identity=email, expires_delta=timedelta(minutes=15))
            refresh_token = create_refresh_token(identity=email, expires_delta=timedelta(days=1))
            return make_response(jsonify({"message": "You have login successfully!",
                                          "access_token": access_token,
                                          "refresh_token": refresh_token,
                                          "user": {
                                              "role": already_user["role"],
                                              "company_name": already_user["company_name"],
                                              "company_id": already_user["company_id"],
                                              "name": already_user["name"],
                                              "email": already_user["email"],
                                              "verified": already_user["verified"]
                                          }
                                          }), 200)
        except Exception as e:
            return make_response(jsonify({'error': str(e)}), 500)


class UserAdd(Resource):
    """This api is used to add new users with specified role"""

    @jwt_required()
    def post(self):
        try:
            admin_email = get_jwt_identity()
            name = request.json.get("name", None)
            email = request.json.get("email", None)
            role_id = request.json.get("role", None)
            verified = False

            if name in [None, ""] or email in [None, ""] or role_id in [None, ""]:
                return make_response(jsonify({"message": "Please provide all necessary information."}), 200)

            already_user_admin = find_user(admin_email)
            if not already_user_admin:
                return make_response(jsonify({"message": "User with provided email does not exist."}), 200)

            if already_user_admin["role"]["role_name"] != "Admin":
                return make_response(jsonify({"message": "Only Admin can add new users"}), 200)

            already_user = find_user(email)
            if already_user:
                return make_response(jsonify({"message": "User with provided email already exist."}), 200)

            all_values = {
                "name": name,
                "email": email,
                "role": ObjectId(role_id),
                "company_name": already_user_admin["company_name"],
                "company_id": already_user_admin["company_id"],
                "verified": verified
            }

            expire_token_time = datetime.now() + timedelta(minutes=15)
            expire_epoch_time = int(expire_token_time.timestamp())
            made_payload = {"email": email, "exp": expire_epoch_time}
            made_verification_token = jwt.encode(made_payload, "sumeet", algorithm="HS256")

            if add_new_user(all_values):
                send_mail.delay(email, made_verification_token)
                return make_response(jsonify({"message": "New user has been added successfully. A mail has been sent "
                                                         "to provided user email for verification."}), 200)

        except Exception as e:
            return make_response(jsonify({"error": str(e)}), 500)


api.add_resource(UserRegister, "/user/register")
api.add_resource(UserVerify, "/user/verify")
api.add_resource(UserSetPassword, "/user/set-password")
api.add_resource(UserLogin, "/user/login")
api.add_resource(UserAdd, "/user")


