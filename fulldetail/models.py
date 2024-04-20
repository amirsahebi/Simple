from django.db import models

# Create your models here.

class Profile(models.Model):
    accountaddress = models.CharField(max_length=200,blank=True,default="")
    userid = models.IntegerField(blank= True,null= True)
    name = models.CharField(max_length=200,blank=True,default="")
    bio = models.CharField(max_length=200,blank=True,default="")
    loc = models.CharField(max_length=200,blank=True,default="")
    joined = models.CharField(max_length=200,blank=True,default="")
    followers = models.IntegerField(blank= True,null= True)
    following = models.IntegerField(blank= True,null= True)
    tweet_num = models.IntegerField(blank= True,null= True)
    processfield = models.ForeignKey('Process',blank=True,null=True,on_delete=models.CASCADE)
    profile_image_url =  models.CharField(max_length=200,blank=True,default="")
    created_at = models.DateTimeField(auto_now_add=True,null=True,blank=True)

class Tweet(models.Model):
    profile = models.ForeignKey('Profile',blank=True,null=True,on_delete=models.CASCADE)
    text = models.CharField(max_length=10000,blank=True,default="")
    created_at = models.CharField(null=True,blank=True,max_length=250)

class Process(models.Model):
    description = models.CharField(max_length=200,blank=True,null=True)
    is_open = models.BooleanField(default=False)
    count = models.IntegerField()
    twtcount = models.IntegerField(null=True,blank=True)
    repeated_count = models.IntegerField(null=True,blank=True)
    success_count = models.IntegerField(null=True,blank=True)
    duration = models.IntegerField(null=True,blank=True)
    percentage = models.IntegerField(null=True,blank=True)
    until = models.CharField(null=True,blank=True,max_length=250)
    since = models.CharField(null=True,blank=True,max_length=250)
    created_at = models.DateTimeField(auto_now_add=True)