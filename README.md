# sample_authentication

How to Run :
- Install Python 3 and pip and postgreSQL
- use the command : pip install -r requirements.txt
- configure the database setting in settings.py file according to your database
- use the command : python manage.py migrate
- use the command : python manage.py runserver

User Roles :
- admin
- teacher
- student

Postman collection link :
- https://www.getpostman.com/collections/6b24c1873b10bac60799

API Endpoints :
- api/login/                            ## Retrives JWT token for a user
- api/university/signup/                ## Registers admin
- api/university/list-user/             ## List the users present in database (requires  JWT token)
- api/university/create-user/           ## add user into the database (requires JWT token)
- api/university/forgot-password/       ## reset password 
