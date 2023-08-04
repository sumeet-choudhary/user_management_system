from celery import Celery
import os


def make_celery(application):
    celery_app = Celery(application, broker=os.getenv('RABBITMQ_URI'), include=['application.celery_config.celery_task'])
    return celery_app
