from django.db import models

# Create your models here.

class Token(models.Model):
    tokenaddress = models.CharField(max_length=200,blank=True,default="")
    name = models.CharField(max_length=200,blank=True,default="")
    active_fulldata = models.BooleanField(default=False)
    active_labeling = models.BooleanField(default=False)
    active_getuser = models.BooleanField(default=False)
    active_tweettrack = models.BooleanField(default=False)
    reset_day = models.IntegerField()
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True,blank=True)
