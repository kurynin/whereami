from django.db import models
from django.contrib.auth.models import User


class Request(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.CharField(max_length=80)
    result = models.CharField(max_length=80, null=True)
    creation_date = models.DateTimeField(auto_now_add=True)


class TMP(models.Model):
    text = models.CharField(max_length=50)
