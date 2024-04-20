from django.db import models

# Create your models here.

class Profile(models.Model):
    accountaddress = models.CharField(max_length=200,blank=True,default="")
    parent = models.ForeignKey('self',blank=True,null=True,default=None,on_delete=models.CASCADE)
    processfield = models.ForeignKey('Process',blank=True,null=True,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class NotAcceptedProfile(models.Model):
    accountaddress = models.CharField(max_length=200,blank=True,default="")
    accountid = models.CharField(max_length=200,blank=True,default="")
    processfield = models.ForeignKey('Process',blank=True,null=True,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)



class Process(models.Model):
    is_open = models.BooleanField(default=False)
    starting_node = models.ForeignKey('Profile',blank=True,null=True,on_delete=models.CASCADE)
    count = models.IntegerField()
    reviewed_count = models.IntegerField()
    duration = models.IntegerField(null=True,blank=True)
    percentage = models.IntegerField(null=True,blank=True)
    created_at = models.CharField(null=True,blank=True,max_length=250)
    max_result = models.IntegerField(null=True,blank=True)
    succces_percent = models.IntegerField(null=True,blank=True)
    succces_count = models.IntegerField(null=True,blank=True)
    description = models.CharField(null=True,blank=True,max_length=250)
