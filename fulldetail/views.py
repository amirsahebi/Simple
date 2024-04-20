
from fulldetail.models import Process, Tweet, Profile
import logging
from django.http import FileResponse
import time
import datetime
from .models import Process, Profile
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
import random
from asgiref.sync import async_to_sync
import shutil
import datetime
from channels.layers import get_channel_layer
import requests
import os
import pandas as pd
import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from .models import Profile
from tqdm import tqdm
import os, requests
import urllib.parse
from tokenmanager.models import Token

logger = logging.getLogger('general')

# Create your views here.

# Convet excel file to list and return it
def import_data(impoted_file):              
    try:  
        myfile = impoted_file       
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)
        excel_file = uploaded_file_url
        excel_file = urllib.parse.unquote(excel_file) 
        empexceldata = list(pd.read_excel("."+excel_file).user.dropna())
        os.remove("."+excel_file)
        return empexceldata
    except Exception as e:            
        print(e)
        logger.error(f"Error in import_data function:{e}")
     
# Get all data of one twitter profile and return it
def get_details(username,token_list,token_selected,twtcount,since,until):
    try:
        until = (datetime.datetime.strptime(until,'%a, %d %b %Y %X GMT')).strftime('%Y-%m-%dT%H:%M:%S.000Z')
        if since != 'null':
            since = (datetime.datetime.strptime(since,'%a, %d %b %Y %X GMT')).strftime('%Y-%m-%dT%H:%M:%S.000Z')
        print(token_selected)
        print(username)
        token = token_list[token_selected]
        user = requests.get(f"https://api.twitter.com/2/users/by/username/{username}?user.fields=created_at,description,entities,id,location,name,pinned_tweet_id,profile_image_url,protected,public_metrics",headers=token).json()
        id = user["data"]["id"]
        if user["data"].get("location") is not None:
            location = user["data"]["location"]
        else:
            location = ""
        if user["data"].get("description") is not None:
            bio = user["data"]["description"]
        else:
            bio = ""
        protected = user["data"]["protected"]
        followers_count = user["data"]["public_metrics"]["followers_count"]
        following_count = user["data"]["public_metrics"]["following_count"]
        tweet_count = user["data"]["public_metrics"]["tweet_count"]
        created_at = user["data"]["created_at"]
        if user["data"].get("profile_image_url") is not None:
            profile_image_url = user["data"]["profile_image_url"]
        else:
            profile_image_url = ""
        name = user["data"]["name"]
        if since == 'null':
            response = requests.get(f"https://api.twitter.com/2/users/{id}/tweets?max_results=100&tweet.fields=lang,created_at&exclude=retweets&end_time={until}",headers=token).json()
        else:
            response = requests.get(f"https://api.twitter.com/2/users/{id}/tweets?max_results=100&tweet.fields=lang,created_at&exclude=retweets&start_time={since}&end_time={until}",headers=token).json()
        result = []
        result += response["data"]
        if twtcount is None:
            twtcount = 500
        if tweet_count > 100:
            while response['meta'].get("next_token") is not None and len(result)<=twtcount and response['meta']['result_count'] > 0:
                if response['meta'].get("next_token") is not None:
                    pagination = response['meta']["next_token"]
                    response = get_tweets(id,pagination,token_list,token_selected,since,until)
                    result += response["data"]
        tweets = []
        for tweet in result:
            if tweet["lang"] == "fa":
                tweets.append({"text":tweet["text"],"created_at":tweet["created_at"]})
        
        return({"id":id,"bio":bio,"protected":protected,"followers_count":followers_count,"following_count":following_count,"loc":location,"tweet_count":tweet_count,"joined":created_at,"profile_image_url":profile_image_url,"name":name,"tweets":tweets,"token_selected":token_selected})
    except Exception as e:
        try:
            print("error in get_details",e)
            print(token)
            logger.error(f"Error in get_details function: with token {token}")
            logger.error(f"Error in get_details function: {e}")
            logger.error(f"Error in get_details function: https://api.twitter.com/2/users/by/username/{username}?user.fields=created_at,description,entities,id,location,name,pinned_tweet_id,profile_image_url,protected,public_metrics:  {user}")
            if user.get("data") is not None:
                logger.error(f"Error in get_details function: https://api.twitter.com/2/users/{id}/tweets?max_results=100&tweet.fields=lang,created_at&exclude=retweets:  {response}")
                print(response)   
            print(user)
            if check_limits(user):
                print("user1",token_selected)
                token_selected = (token_selected+1)%(len(token_list))
                print("user2",token_selected)
                return get_details(username,token_list,token_selected)
            elif check_authorization(user):
                return {"token_selected":token_selected}
            elif check_limits(response):
                print("response1",token_selected)
                token_selected = (token_selected+1)%(len(token_list))
                print("response2",token_selected)
                return get_details(username,token_list,token_selected)
            elif check_authorization(response):
                return {"token_selected":token_selected}
            else:
                return {"token_selected":token_selected}
        except Exception as e1:
            print(e1)
            logger.error(f"Error in get_details function: {e}")
            return {"token_selected":token_selected}


# Function for checking twitter api if can't access to profile 
def check_authorization(data):
    if data.get('errors') is not None:
        for error in data.get('errors'):
            if error.get('title') is not None:
                if error['title'] == 'Authorization Error':
                    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!","Authorization Error","!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!",time.localtime())
                    return True
    elif data.get('errors') is not None:
        for error in data.get('errors'):
            if error.get('title') is not None:
                if error['title'] == 'Forbidden':
                    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!","Authorization Error","!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!",time.localtime())
                    return True
    return False

# Get all tweets of one profile and return it
def get_tweets(id,pagination,token_list,token_selected,since,until):
    try:
        token = token_list[token_selected]
        if since == 'null':
            response = requests.get(f"https://api.twitter.com/2/users/{id}/tweets?max_results=100&tweet.fields=lang,created_at&exclude=retweets&pagination_token={pagination}&end_time={until}",headers=token).json()
        else:
            response = requests.get(f"https://api.twitter.com/2/users/{id}/tweets?max_results=100&tweet.fields=lang,created_at&exclude=retweets&pagination_token={pagination}&start_time={since}&end_time={until}",headers=token).json()
        return response
    except Exception as e:
        print(e)
        logger.error(f"Error in get_tweets function: {e}")
        logger.error(f"Error in get_tweets function: https://api.twitter.com/2/users/{id}/tweets?max_results=100&tweet.fields=lang,created_at&exclude=retweets:  {response}")
        if check_limits(response):
            token_selected = (token_selected+1)%(len(token_list))
            return get_tweets(id,pagination,token_list,token_selected)

# Check if api responsed too many request
def check_limits(data):
    if data.get('title') is not None:
            if data['title'] == 'Too Many Requests' or data['title'] == 'UsageCapExceeded':
                print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!","limit error","!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!",time.localtime())
                duration = random.randint(0, 10)
                time.sleep(duration)
                return True
    return False

# Export zip file as response to send it to client
class Export_Parquets(APIView):
    def get(self, request, *args, **kwargs):
        time = export_data(self.kwargs["id"],False)
        print(time)
        print("finish!!!!!!!")
        return FileResponse(
            open(f"./{time}_GET_FULLDATA.zip", 'rb'),
            as_attachment=True,
            filename=f'{time}_GET_FULLDATA.zip'
        )

class Export_Pictures(APIView):
    def get(self, request, *args, **kwargs):
        time = export_data(self.kwargs["id"],False)
        print(time)
        print("finish!!!!!!!")
        return FileResponse(
            open(f"./{time}_GET_FULLDATA_PICTURES.zip", 'rb'),
            as_attachment=True,
            filename=f'{time}_GET_FULLDATA_PICTURES.zip'
        )

# Class for returing recordings with their download and update urls
class History(APIView):
    def get(self, request, *args, **kwargs):
        all_processes =  Process.objects.filter(is_open = False).order_by("id")
        data = []
        if len(all_processes) > 0:
            for process in all_processes:
                data.append({
                    "id":process.id,
                    "description":process.description,
                    "created_at":process.created_at,
                    "count":process.count,
                    "duration":process.duration,
                    "success_count":process.success_count,
                    "repeated_count":process.repeated_count,
                    "percentage":process.percentage,
                    "export_parquets_url":f"https://new.amir1380.tk/fulldata/exportparquets/{process.id}/",
                    "export_pictures_url":f"https://new.amir1380.tk/fulldata/exportpictures/{process.id}/",
                    "update_url":f"https://new.amir1380.tk/fulldata/update/{process.id}/"
                }
                )
        else:
            data = False
        return Response({"processes":data})

# Export data from database to excel and images folder
def export_data(id,is_updating):
    try:
        process = Process.objects.get(id = id)
        time = process.created_at.strftime("%m_%d_%Y_%H_%M_%S")

        # Check if zip file has been created and not in updating situation
        if os.path.isfile(f"./{time}_GET_FULLDATA.zip") and (not is_updating):
            return time
        
        columns = ['user','id','twts','name','bio','loc','Joined','followers_count','following_count','tweet_num','get_at','created_at']
        
        # Get Profiles of the selected proccess
        process = Process.objects.get(id = id)
        time = process.created_at.strftime("%m_%d_%Y_%H_%M_%S")
        profiles = Profile.objects.filter(processfield = process)
        
        # If folder exist delete it
        if os.path.isdir(f"./{time}_GET_FULLDATA"):
            shutil.rmtree(f"./{time}_GET_FULLDATA")

        if os.path.isdir(f"./{time}_GET_FULLDATA_PICTURES"):
            shutil.rmtree(f"./{time}_GET_FULLDATA_PICTURES")

        # Create main and subfolder
        os.mkdir(f"./{time}_GET_FULLDATA/")
        os.mkdir(f"./{time}_GET_FULLDATA_PICTURES/")
        
        # Get particular count and images of all accounts
        n = 0
        count = 0
        while not(n == len(profiles)):
            count +=1
            df = pd.DataFrame(columns=columns)
            for _ in range(10):
                if n == len(profiles):
                    break
                print(n)
                profile = profiles[n]

                if not (profile.profile_image_url == ""):
                    url = profile.profile_image_url.replace("_normal","")
                    get_image(url,time,profile.userid)
                    
                if Tweet.objects.filter(profile = profile).exists():
                    queryset = Tweet.objects.filter(profile = profile).values_list('profile__accountaddress','profile__userid','text','profile__name','profile__bio','profile__loc','profile__joined','profile__followers','profile__following','profile__tweet_num','profile__created_at','created_at')
                    df1 = pd.DataFrame(list(queryset),columns=columns)
                    # def make_clickable(time,userid):
                    #     return f'<a href="file:///../{time}_GET_FULLDATA_PICTURES/{userid}.jpg" rel="noopener noreferrer" target="_blank">link</a>'
                    # df1['image'] = df1.apply(lambda x: make_clickable(time,x["image"]), axis=1)
                    # df1.style

                    def make_string(date):
                        return date.strftime("%m_%d_%Y_%H_%M_%S")
                    df1['get_at'] = df1.apply(lambda x: make_string(x["get_at"]), axis=1)
                    df = pd.concat([df,df1],ignore_index=True)
                n += 1
                

            df.to_parquet(f"./{time}_GET_FULLDATA/{time}_GET_FULLDATA({count}).parquet")


        
        shutil.make_archive(f"./{time}_GET_FULLDATA", 'zip', f"./{time}_GET_FULLDATA")
        shutil.make_archive(f"./{time}_GET_FULLDATA_PICTURES", 'zip', f"./{time}_GET_FULLDATA_PICTURES")
        shutil.rmtree(f"./{time}_GET_FULLDATA")
        shutil.rmtree(f"./{time}_GET_FULLDATA_PICTURES")

        print("time:",time)
        return time
    except Exception as e:
        print(e)
        print("error in export_data",e)
        logger.error(f"Error in export_data function: {e}")


# Get image and download it
def get_image(url,time1,id):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            with open(f"./{time1}_GET_FULLDATA_PICTURES/{id}.jpg", 'wb') as f:
                f.write(response.content)
        return response
    except Exception as e:
        print(url)
        print("Error in get_image Function:",e)
        duration = random.randint(0, 10)
        time.sleep(duration)
        return get_image(url,time1,id)


# Main class for getting full data of all accounts
class FullData(APIView):
    # permission_classes = (IsAuthenticated,)
    def post(self, request, *args, **kwargs):
        try:
            tokens = Token.objects.filter(active = True,active_fulldata = True)
            print(tokens)
            token_list = []
            for token in tokens:
                token_list.append({"Authorization":f"Bearer {token.tokenaddress}"})
            layer = get_channel_layer()
            token_selected = 0
            myfile = request.FILES['excel_file']
            description = request.POST.get('description')
            twtcount = request.POST.get('twtcount')
            since = request.POST.get('since')
            until = request.POST.get('until')
            print(since)
            print(type(since))
            twtcount = int(twtcount)
            accountaddresses = import_data(myfile)
            accountaddresses_count = len(accountaddresses)
            process = Process.objects.create(is_open = True,count = 0,description = description,twtcount = twtcount,since = since, until = until)
            t1 = datetime.datetime.now()
            count = 0
            success_count = 0
            repeated_count = 0
            percent = 0
            for accountaddress in tqdm(accountaddresses):
                print("")
                count += 1
                account = get_details(accountaddress,token_list,token_selected,twtcount,since,until)
                token_selected = account["token_selected"]
                
                
                if Profile.objects.filter(accountaddress = accountaddress):
                    repeated_count += 1

                if account.get('id') is not None:
                    this_profile = Profile.objects.create(accountaddress = accountaddress,name = account["name"],bio = account["bio"],loc = account["loc"],joined = account["joined"],followers = account["followers_count"],following = account["following_count"],tweet_num = account["tweet_count"],profile_image_url = account["profile_image_url"],userid = account['id'],processfield = process)
                    for tweet in account["tweets"]:
                        Tweet.objects.create(text = tweet["text"],created_at = tweet["created_at"],profile = this_profile)
                    success_count += 1
                print(count)
                print(accountaddress)
                print(((count)/accountaddresses_count)*100)
                percent = int(((count)/accountaddresses_count)*100)
                process.count = count
                process.success_count =success_count
                process.repeated_count = repeated_count
                process.percentage = percent
                process.save()
                async_to_sync(layer.group_send)("dashboard", {"type": "send_count", "percent": percent,"is_open":True,"created_at":process.created_at.strftime("%m/%d/%Y, %H:%M:%S"),"count":count,"id":process.id,"description":description,"success_count":success_count,"repeated_count":repeated_count})
            t2 = datetime.datetime.now()
            process.duration = ((t2-t1).seconds)//60
            process.is_open = False
            process.save()
            async_to_sync(layer.group_send)("dashboard", {"type": "send_count", "percent": percent,"is_open":False,"created_at":process.created_at.strftime("%m/%d/%Y, %H:%M:%S"),"count":count,"id":process.id,"description":description})
            a = export_data(process.id,False)
            print("vvvvvvvvvvvvvvv")
            return Response({"result":a})
        except Exception as e:
            t2 = datetime.datetime.now()
            process.duration = ((t2-t1).seconds)//60
            process.is_open = False
            process.save()
            print(e)
            print("error in FullData",e)
            logger.error(f"Error in FullData class: {e}")
            async_to_sync(layer.group_send)("dashboard", {"type": "send_count", "percent": percent,"is_open":False,"created_at":process.created_at.strftime("%m/%d/%Y, %H:%M:%S"),"count":count,"id":process.id,"description":description})
        
# Main class for updating all selected account
class UpdateData(APIView):
    def get(self, request, *args, **kwargs):
        try:
            tokens = Token.objects.filter(active = True,active_fulldata = True)
            print(tokens)
            token_list = []
            for token in tokens:
                token_list.append({"Authorization":f"Bearer {token.tokenaddress}"})
            layer = get_channel_layer()
            token_selected = 0
            
            process = Process.objects.get(id = self.kwargs["id"])
            time = process.created_at.strftime("%m_%d_%Y_%H_%M_%S")

            # Delete zip file if exist
            if os.path.isfile(f"./{time}_GET_FULLDATA.zip"):
                os.remove(f"./{time}_GET_FULLDATA.zip")

            # Creating profiles
            profiles = Profile.objects.filter(processfield = process)
            t1 = datetime.datetime.now()
            count = 0
            success_count = 0
            percent = 0
            for profile in tqdm(profiles):
                print("")
                count += 1
                account = get_details(profile.accountaddress,token_list,token_selected,process.twtcount)
                token_selected = account["token_selected"]

                if account.get('id') is not None:
                    new_profile = Profile.objects.create(accountaddress = profile.accountaddress,name = account["name"],bio = account["bio"],loc = account["loc"],joined = account["joined"],followers = account["followers_count"],following = account["following_count"],tweet_num = account["tweet_count"],profile_image_url = account["profile_image_url"],userid = account['id'],processfield = process)
                    profile.delete()
                    
                    # Create tweets objects
                    for tweet in account["tweets"]:
                        Tweet.objects.create(text = tweet["text"],created_at = tweet["created_at"],profile = new_profile)
                    success_count += 1
                percent = int(((count)/len(profiles))*100)
                process.count = count
                process.success_count =success_count
                process.percentage = percent
                process.save()
                async_to_sync(layer.group_send)("dashboard", {"type": "send_count", "percent": percent,"is_open":True,"created_at":process.created_at.strftime("%m/%d/%Y, %H:%M:%S"),"count":count,"id":process.id,"description":process.description,"success_count":success_count,"repeated_count":process.repeated_count})
            t2 = datetime.datetime.now()
            process.duration = ((t2-t1).seconds)//60
            process.is_open = False
            process.save()
            async_to_sync(layer.group_send)("dashboard", {"type": "send_count", "percent": percent,"is_open":False,"created_at":process.created_at.strftime("%m/%d/%Y, %H:%M:%S"),"count":count,"id":process.id,"description":process.description,"success_count":success_count,"repeated_count":process.repeated_count})
            a = export_data(process.id,True)
            return Response({"result":a})
        except Exception as e:
            t2 = datetime.datetime.now()
            process.duration = ((t2-t1).seconds)//60
            process.is_open = False
            process.save()
            async_to_sync(layer.group_send)("dashboard", {"type": "send_count", "percent": percent,"is_open":False,"created_at":process.created_at.strftime("%m/%d/%Y, %H:%M:%S"),"count":count,"id":process.id,"description":process.description,"success_count":success_count,"repeated_count":process.repeated_count})
            print(e)
            print("error in UpdateData",e)
            logger.error(f"Error in UpdateData class: {e}")

class GetTemplate(APIView):
    def get(self, request, *args, **kwargs):
        return FileResponse(
            open(f"./Template.xls", 'rb'),
            as_attachment=True,
            filename='Template.xls'
        )

class DeleteProcess(APIView):
    def post(self, request, *args, **kwargs):
        id = request.POST.get('id')
        process = Process.objects.get(id = id)

        process.delete()

        return Response({"deleted":True})


