from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, Group, Permission

# Expense Models
class Expense(models.Model):
    expenseName = models.CharField(max_length=200)
    expenseCategory = models.CharField(max_length=200, null=True)
    expenseCost = models.DecimalField(max_digits=10, decimal_places=2)
    expenseFrequency = models.CharField(max_length=200)

class Tester(models.Model):
    name = models.CharField(max_length=30)
    email = models.CharField(max_length=200)

# User Authentication
class AppUserManager(BaseUserManager):
	def create_user(self, email, password=None):
		if not email:
			raise ValueError('An email is required.')
		if not password:
			raise ValueError('A password is required.')
		email = self.normalize_email(email)
		user = self.model(email=email)
		user.set_password(password)
		user.save()
		return user
	def create_superuser(self, email, password=None):
		if not email:
			raise ValueError('An email is required.')
		if not password:
			raise ValueError('A password is required.')
		user = self.create_user(email, password)
		user.is_superuser = True
		user.save()
		return user


class AppUser(AbstractBaseUser, PermissionsMixin):
	user_id = models.AutoField(primary_key=True)
	email = models.EmailField(max_length=50, unique=True)
	username = models.CharField(max_length=50)
	# groups = models.ManyToManyField(Group, related_name='app_users')
	# user_permissions = models.ManyToManyField(Permission, related_name='app_users_permissions')
	USERNAME_FIELD = 'email'
	REQUIRED_FIELDS = ['username']
	objects = AppUserManager()
	def __str__(self):
		return self.username