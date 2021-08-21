from django.shortcuts import render
from university.models import *
import json,time,datetime
from django.contrib.auth.hashers import make_password
from . import serializers
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view,permission_classes

# Create your views here.

'''
API Name : sign_up
Description : Used for initial sign up for admins
Authentication : No auth required
'''
@csrf_exempt
@api_view(['POST'])
def sign_up(request):
   try:
      data = json.loads(request.body)
      print(data)
      # check if user exists
      user = Users.objects.filter(email_id = data['email_id'],is_deleted =False)
      if user and user.count > 0:
         return_object={
            "status":409,
            "message":"User already exists"
         }
         return JsonResponse(return_object, safe = False)      
      user_obj = Users()
      user_status = map_user_data(user_obj,data)
      if user_status and type(user_status) == dict:
         return_object={
            "status":200,
            "message":"user created Successfully",
            "user_id": user_status
         }
      else:
         return_object={
            "status":500,
            "message":"Error creating user",
            "error":user_status
         }
   except (Exception) as error:
      print("create user error : ",error)
      return_object={
            "status":500,
            "message":"Error creating user"
         }
   return JsonResponse(return_object, safe = False)

'''
API Name : forgot_password
Description : Used for resetting password
Body :
      username
      new_password
'''
@csrf_exempt
@api_view(['POST'])
def forgot_password(request):
   try:
      data = json.loads(request.body)
      print(data)
      # check if user exists
      user_object = Users.objects.filter(email_id = data['username'],is_deleted =False ).first()
      user_auth_obj = User.objects.filter(username = data['username']).first()
      if not user_object and len(user_object) < 0 and not user_auth_obj and len(user_auth_obj) < 0 :
         return_object={
            "status":500,
            "message":"User does not exists"
         }
         return JsonResponse(return_object, safe = False) 
      
      #changing password from user input
      password = make_password(data['new_password'])
      user_object.password = password
      user_auth_obj.password = password
      user_auth_obj.save()
      user_object.save()
      return_object={
            "status":200,
            "message":"Password Changed Successfully",
            "password": data['new_password']
         }
   except (Exception) as error:
      print("create user error : ",error)
      return_object={
            "status":500,
            "message":"Error resetting password",
            "error":str(error)
         }
   return JsonResponse(return_object, safe = False)

'''
API Name : list_user
Description : Used for listing the users in the database
Headers :
         Authorization : JWT access token required with 'Bearer ' prefix
Body :
      user_id (optional)
      user_role (optional)
      email_id (optional)
'''
@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def list_user(request):
   try:
      data = json.loads(request.body)
      print('user',request.user)
      # Authorizing user by checking it's user role
      user_obj = Users.objects.filter(is_deleted = False,email_id = request.user).first()
      if not user_obj:
         return_object={
            "status":500,
            "message":"User not found"
         }
         return JsonResponse(return_object, safe = False)
      user_list = fetch_user_data(data,user_obj)
      if user_list :
         results = list(user_list.values('id','user_id','user_role','first_name','last_name','email_id','is_deleted','created_at'))  
      else:
         results = []
      return_object={
            "status":200,
            "message":"Successfully Retrived",
            "results":results
         }
   except (Exception) as error:
      print("Error while fetching user : ",error)
      return_object={
            "status":500,
            "message":"Error fetching user"
         }
   return JsonResponse(return_object, safe = False)


'''
API Name : create_user
Description : Used for creating the users in the database
Headers :
         Authorization : JWT access token required with 'Bearer ' prefix
Body :
      email_id
      first_name
      last_name
      user_role
      password

'''
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def create_user(request):
   try:
      data = json.loads(request.body)
      # check if user exists
      user = Users.objects.filter(email_id = data['email_id'],is_deleted =False )
      if user and user.count > 0:
         return_object={
            "status":409,
            "message":"User already exists"
         }
         return JsonResponse(return_object, safe = False)  

      # Check Authorization of the user 
      user_auth_obj = Users.objects.filter(is_deleted = False,email_id = request.user).first()
      check_authorization = check_authorization_for_adding_user(user_auth_obj,data)
      if check_authorization and check_authorization['status'] =='fail':
         return_object={
            "status":403,
            "message":check_authorization['message']
         }
         return JsonResponse(return_object, safe = False)         

      user_obj = Users()
      user_status = map_user_data(user_obj,data)
      if user_status and type(user_status) == dict:
         return_object={
            "status":200,
            "message":"user created Successfully",
            "credentials": user_status
         }
      else:
         return_object={
            "status":500,
            "message":"Error creating user",
            "error":user_status
         }
   except (Exception) as error:
      print("create user error : ",error)
      return_object={
            "status":500,
            "message":"Error creating user"
         }
   return JsonResponse(return_object, safe = False)

# Checking authorization while adding users
def check_authorization_for_adding_user(user_auth_obj,data):

   if user_auth_obj.user_role =='admin': # admin can add any users
      return {"status":"success","message":"Allowed to add"} 

   elif user_auth_obj.user_role =='teacher': # teacher can only add students
      if data['user_role'] == "student":
         return {"status":"success","message":"Allowed to add"} 
      else:
         return {"status":"fail","message":"teacher can only add students"} 

   elif user_auth_obj.user_role =='student':
      return {"status":"fail","message":"students not allowed to add users"}  

   else :
      return {"status":"fail","message":"user role is not present or invalid"}        


# Function to fetch user data based on user role
def fetch_user_data(data,user_obj):
   try:
      # Authorizing search based on the user role

      if user_obj.user_role == 'admin':   # can search all the users
         list_user = Users.objects.filter(is_deleted = False)
         if 'user_id' in data and data['user_id']:
            list_user = list_user.filter(user_id = data['user_id'].lower())
         if 'email_id' in data and data['email_id']:
            list_user = list_user.filter(email_id = data['email_id'].lower())
         if 'user_role' in data and data['user_role']:
            list_user = list_user.filter(user_role = data['user_role'].lower())            
         
      elif user_obj.user_role == 'teacher': # can search only students
         print('2nd condition')
         list_user = Users.objects.filter(is_deleted = False,user_role = 'student')
         print(list_user)
         if 'user_id' in data and data['user_id']:
            list_user = list_user.filter(user_id = data['user_id'].lower(),is_deleted = False,user_role = 'student')
         if 'email_id' in data and data['email_id']:
            list_user = list_user.filter(email_id = data['email_id'].lower(),is_deleted = False,user_role = 'student')

      elif user_obj.user_role == 'student': # can search only his own details
         list_user = Users.objects.filter(user_id = user_obj.luser_id,is_deleted = False,user_role = 'student')
      
      return list_user
   except (Exception) as error:
      print("fetch_user_data : ",error)
      return False

# Common function for mapping user data
def map_user_data(user_obj,data):
   try:
      # Mapping user for both tables - django user for authetication and Users table for storing details
      user_id = "U"+str(int(time.time_ns() * 10))
      user_aut_obj = User()
      user_obj.user_id = user_id
      user_obj.created_at = datetime.datetime.now()
      user_obj.first_name = data['first_name']
      user_aut_obj.first_name = data['first_name']
      user_obj.last_name = data['last_name']
      user_aut_obj.last_name = data['last_name']
      email_id = data['email_id'].lower()
      user_obj.email_id = email_id
      user_aut_obj.email = email_id
      user_aut_obj.username = email_id
      if 'user_role' in data and data['user_role']:
         user_obj.user_role = data['user_role'].lower()
         if data['user_role'].lower() == 'admin':
            user_aut_obj.is_superuser = True
            user_aut_obj.is_staff = False
         elif data['user_role'].lower() == 'teacher':
            user_aut_obj.is_superuser = False
            user_aut_obj.is_staff = True
         elif data['user_role'].lower() == 'admin':
            user_aut_obj.is_superuser = False
            user_aut_obj.is_staff = True         
      if 'password' in data and data['password']: 
         password = make_password(data['password'])
         user_obj.password = password
         user_aut_obj.password = password
      user_obj_status = user_obj.save()
      user_aut_obj_status = user_aut_obj.save()
      
      return {"user_id":user_id,"username":email_id,"password":data['password']}
   except (Exception) as error:
      print("map_user_data : ",error)
      return error