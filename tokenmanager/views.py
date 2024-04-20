import logging
from django.http import FileResponse
import time
import datetime
from .models import Token
from rest_framework.views import APIView
from rest_framework.response import Response
import random
from asgiref.sync import async_to_sync
import shutil
import datetime
import os
import pandas as pd
import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from tqdm import tqdm
import os, requests
import urllib.parse
from dateutil import relativedelta

logger = logging.getLogger('general')

# Create your views here.

# Convet excel file to list and return it
class Tokenlist(APIView):
    def post(self, request, *args, **kwargs):
        tokens = Token.objects.all().order_by("active")
        data = []
        for token in tokens:
            token1 = {"Authorization":f"Bearer {token.tokenaddress}"}
            user = requests.get("https://api.twitter.com/2/users/44196397/tweets?max_results=100&tweet.fields=lang&exclude=retweets",headers=token1).json()
            if user.get("title"):
                if user["title"] == "UsageCapExceeded":
                    token.active = False
                    token.save()
            else:
                token.active = True
                token.save()

            if datetime.datetime.now().day >= token.reset_day:
                rest_days = ((datetime.date.today().replace(day=token.reset_day) + relativedelta.relativedelta(months=1))-datetime.date.today()).days
            elif datetime.datetime.now().day < token.reset_day:
                rest_days = (token.reset_day - datetime.datetime.now().day)
            data.append({
                'id':token.id,
                'name':token.name,
                'tokenaddress':token.tokenaddress,
                'active':token.active,
                'reset_day':rest_days,
                'active_fulldata':token.active_fulldata,
                'active_labeling':token.active_labeling,
                'active_getuser':token.active_getuser,
                'active_tweettrack':token.active_tweettrack
            })
        return Response(data)

class AddToken(APIView):
    def post(self, request, *args, **kwargs):
        try:
            tokenaddress = request.POST.get('tokenaddress')
            token = {"Authorization":f"Bearer {tokenaddress}"}
            print("heloo")
            user = requests.get("https://api.twitter.com/2/users/by/username/elonmusk",headers=token).json()
            name = request.POST.get('name')
            reset_day = int(request.POST.get('reset_time'))
            print(user)
            if user["data"]["username"] == "elonmusk" and not Token.objects.filter(tokenaddress = tokenaddress).exists():
                print("okay")
                token = Token.objects.create(name = name, tokenaddress = tokenaddress,reset_day = reset_day)
                success = True
            else:
                success = False

            return Response({"success":success})

        except Exception as e:
            print(e)
            return Response({"success":False})
        
             

class Activate(APIView):
    def post(self, request, *args, **kwargs):
        app = request.POST.get('app')
        id = request.POST.get('id')
        token = Token.objects.get(id = id)

        if app == 'fulldata':
            token.active_fulldata = True
        elif app == 'getuser':
            token.active_getuser = True
        elif app == 'labeling':
            token.active_labeling = True
        elif app == 'tweettrack':
            token.active_tweettrack = True
        
        token.save()

        return Response({"token":token.id})


class Deactivate(APIView):
    def post(self, request, *args, **kwargs):
        app = request.POST.get('app')
        id = request.POST.get('id')
        token = Token.objects.get(id = id)

        if app == 'fulldata':
            token.active_fulldata = False
        elif app == 'getuser':
            token.active_getuser = False
        elif app == 'labeling':
            token.active_labeling = False
        elif app == 'tweettrack':
            token.active_tweettrack = False
        
        token.save()

        return Response({"token":token.id})
        
class Delete(APIView):
    def post(self, request, *args, **kwargs):
        id = request.POST.get('id')
        print(id)
        token = Token.objects.get(id = id)

        token.delete()

        return Response({"deleted":True})


        






