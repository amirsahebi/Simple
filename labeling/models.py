from django.db import models


USER_TYPE = (('Male', 'male'), ('Female', 'female'),('Notselected', 'notselected'))
STATUS_TYPE = (('Ok', 'ok'), ('Not okay', 'not okay'))
# Create your models here.

class Profile(models.Model):
    gender = models.CharField(
        max_length=20, choices=USER_TYPE, default='Notselected')
    processfield = models.ForeignKey('Process',blank=True,null=True,on_delete=models.CASCADE)
    accountaddress = models.CharField(max_length=200,blank=True,default="")
    age_low = models.IntegerField(blank= True,null= True)
    age_high = models.IntegerField(blank= True,null= True)
    tweet_count = models.IntegerField(blank= True,null= True)
    bio = models.CharField(max_length=200,blank=True,default="")
    status = models.CharField(
        max_length=20, choices=STATUS_TYPE)
    description = models.CharField(max_length=200,blank=True,default="")
    labeled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(null= True,blank= True)
    flag = models.IntegerField(null=True,blank=True,default=0)

    def __str__(self):
        return self.accountaddress



class Process(models.Model):
    is_open = models.BooleanField(default=False)
    count = models.IntegerField(null=True,blank=True)
    low_age_percentage = models.IntegerField(null=True,blank=True)
    high_age_percentage = models.IntegerField(null=True,blank=True)
    gender_percentage = models.IntegerField(null=True,blank=True)
    wanted_percentage = models.IntegerField(null=True,blank=True)
    low_age_check = models.BooleanField(default=False)
    high_age_check = models.BooleanField(default=False)
    gender_check = models.BooleanField(default=False)
    created_at = models.CharField(null=True,blank=True,max_length=250)
    description = models.CharField(null=True,blank=True,max_length=250)
    flag = models.IntegerField(null=True,blank=True,default=0)

class Reason(models.Model):
    reason = models.CharField(null=True,blank=True,max_length=250)