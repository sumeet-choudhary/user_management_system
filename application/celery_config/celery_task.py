import os
from application import celery
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


@celery.task(task_name = "send_mail")
def send_mail(email, made_verification_token):
    email_sender = os.environ.get("EMAIL_SENDER_EMAIL")
    email_sender_password = os.environ.get("EMAIL_SENDER_PASSWORD")
    email_receiver = email

    create_link = f"""
    <html>
      <body>
        <h1><a href='http://127.0.0.1:80/user/verify?token={made_verification_token}'>Your verification link</a></h1>
      </body>
    </html>
    """

    subject = "Dear user please verify your account."
    em = MIMEMultipart("alternative")
    em["FROM"] = email_sender
    em["TO"] = email_receiver
    em["SUBJECT"] = subject

    em_link = MIMEText(create_link, 'html')
    em.attach(em_link)
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(email_sender, email_sender_password)
        smtp.sendmail(email_sender, email_receiver, em.as_string())
