from django.db import models
from django.contrib.auth.models import User


class Status(models.Model):
    name = models.CharField(max_length=20)
    description = models.CharField(max_length=80)


class Request(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    antenna = models.CharField(max_length=80)
    file = models.FileField(default="")
    status = models.ForeignKey(Status, on_delete=models.CASCADE, default="", null=True)
    creation_date = models.DateTimeField(auto_now_add=True)


class Result(models.Model):
    path_to_gga = models.CharField(max_length=300)
    path_to_rtk = models.CharField(max_length=300)
    request_id = models.ForeignKey(Request, on_delete=models.CASCADE, default="", null=True)
