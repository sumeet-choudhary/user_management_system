# user_management_system - 

I have made a user management system:-

User register into the system with company name.
  - That user is automatically given "Admin" role of that particular company.
  - User can verify mail, setup password and login with their information.
  - This "Admin" user can add new users into their respective company assigning certain roles and each role has further permissions added to that role.
  - After addition of new user, that added new user can also verify their mail and also setup password then login. 
  - "Admin" can create, update, delete roles as well as permissions to that role.
  
This project has:-
  - Flask as web framework.
  - REST API's.
  - JWT Token, Access token, Refresh token.
  - Smtplib module to send email (for verification).
  - Nginx as web server.
  - uWSGI as application server.
  - Celery as to run task asynchronous.
  - Rabbitmq which acts as the message broker, to distribute the task to available Celery workers.
  - MongoDB as Database.
  - Docker to contanerize everything.


