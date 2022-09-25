from django.db import models
from django.contrib.auth.models import User
from django.db.models.base import Model
from django.shortcuts import redirect
from django.utils.timezone import datetime
from django.conf import settings
import django.utils
from django.core.exceptions import ValidationError

class custom_alert(models.Model):
	user = models.OneToOneField(User, null = True)
	alert_config = models.TextField(null=True)

class backup_db(models.Model):
	price_now = models.TextField(null=True)
	coin_overall_data = models.TextField(null=True)

class user_profile(models.Model):
	user = models.OneToOneField(User, null = True)
	phone = models.TextField(null=True)
	name= models.CharField(null=True,max_length=200)