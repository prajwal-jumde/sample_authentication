from django.db import models

# Create your models here.
class Users(models.Model):
    available_role = (
        ('admin', 'admin'),
        ('teacher', 'teacher'),
        ('student', 'student'),)

    user_id = models.CharField(max_length=256)
    password = models.CharField(max_length=256)
    user_role = models.CharField(max_length=256,choices=available_role)
    first_name = models.CharField(max_length=256)
    last_name = models.CharField(max_length=256)
    email_id = models.CharField(max_length=256,unique=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(null=True)
    class Meta:
        db_table = 'users'