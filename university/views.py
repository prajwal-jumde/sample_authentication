from django.shortcuts import render

# Create your views here.

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

      user_obj = Users()
      user_id = "U"+str(int(time.time_ns() * 10))
      user_obj.user_id = user_id
      user_obj.created_at = datetime.datetime.now()
      if 'first_name' in data and data['first_name']:
         user_obj.first_name = data['first_name']
      if 'last_name' in data and data['last_name']:
         user_obj.last_name = data['last_name']
      if 'email_id' in data and data['email_id']:
         user_obj.email_id = data['email_id']
      if 'user_role' in data and data['user_role']:
         user_obj.user_role = data['user_role']
      if 'is_deleted' in data and data['is_deleted']:
         user_obj.is_deleted = data['is_deleted']
      
      user_obj_status = user_obj.save()
      if user_obj_status:
         return_object={
            "status":200,
            "message":"user created Successfully",
            "user_id": user_id
         }
   except (Exception) as error:
      print("create user error : ",error)
      return_object={
            "status":500,
            "message":"Error creating user"
         }
   return JsonResponse(return_object, safe = False)