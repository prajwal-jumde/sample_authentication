from django.urls import path,include
from . import views

urlpatterns = [
    path('signup/',views.sign_up),
    path('list-user/',views.list_user),
    path('create-user/',views.create_user),
    path('forgot-password/',views.forgot_password),
    
]
