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

# For admin sign up
@csrf_exempt
def sign_up(request):
   try:
      data = json.loads(request.body)
      print(data)
      # check if user exists
      user = Users.objects.filter(email_id = data['email_id'],is_deleted =False )
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

# def create_user
@csrf_exempt
@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])
def list_user(request):
   try:
      data = json.loads(request.body)
      print('user',request.user)
      # Authorizing user by checking it's user role
      user_obj = Users.objects.filter(is_deleted = False,email_id = request.user)
      if not user_obj:
         return_object={
            "status":500,
            "message":"User not found"
         }
         return JsonResponse(return_object, safe = False)
      user_list = fetch_user_data(data,user_obj)
      return_object={
            "status":200,
            "message":"Successfully Retrived",
            "results":list(user_list.values())
         }
   except (Exception) as error:
      print("Error while fetching user : ",error)
      return_object={
            "status":500,
            "message":"Error fetching user"
         }
   return JsonResponse(return_object, safe = False)

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
         list_user = Users.objects.filter(user_id = data['user_id'].lower(),is_deleted = False,user_role = 'student')
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

def map_user_data(user_obj,data):
   try:
      user_id = "U"+str(int(time.time_ns() * 10))
      user_aut_obj = User()
      user_obj.user_id = user_id
      user_obj.created_at = datetime.datetime.now()
      if 'first_name' in data and data['first_name']:
         user_obj.first_name = data['first_name']
         user_aut_obj.first_name = data['first_name']
      if 'last_name' in data and data['last_name']:
         user_obj.last_name = data['last_name']
         user_aut_obj.last_name = data['last_name']
      if 'email_id' in data and data['email_id']:
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
      
      return {"user_id":user_id,"email_id":email_id,"password":password}
   except (Exception) as error:
      print("fetch_user_data : ",error)
      return error