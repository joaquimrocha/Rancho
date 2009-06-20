from django.db import models
from django.contrib.auth.models import User
from rancho.project.models import Project

class Post(models.Model):
    
    date = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(User, null=True, blank=True)
    message = models.CharField(max_length=1000)
    project = models.ForeignKey(Project, null = True, blank = True)

class ChatData(models.Model):
    
    user = models.ForeignKey(User)
    project = models.ForeignKey(Project, null = True, blank = True) 
    last_request = models.IntegerField()
    is_connected = models.BooleanField(default = False)
