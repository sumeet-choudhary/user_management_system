import os
from flask import Flask
from flask_pymongo import PyMongo
from flask_restful import Api
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
from application.celery_config.make_celery import make_celery
from application.seed import create_default_admin_role
load_dotenv()

app = Flask(__name__)
api = Api(app)
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
app.config["MONGO_URI"] = os.getenv("MONGO_URI")

jwt = JWTManager(app)
mongo = PyMongo(app)
celery = make_celery(app)

create_default_admin_role(mongo)
