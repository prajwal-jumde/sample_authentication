# Generated by Django 3.2.6 on 2021-08-20 17:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('university', '0002_users_password'),
    ]

    operations = [
        migrations.AlterField(
            model_name='users',
            name='user_role',
            field=models.CharField(choices=[('admin', 'admin'), ('teacher', 'teacher'), ('student', 'student')], max_length=256),
        ),
    ]
