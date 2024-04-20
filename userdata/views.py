import logging
from django.http import FileResponse
import time
import json
import datetime
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
from tqdm import tqdm
import os, requests
import urllib.parse

logger = logging.getLogger('general')

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
def get_tweets(id,pagination,token_list,token_selected,limit):
    try:
        token = token_list[token_selected]
        if limit == True:
            response = requests.get(f"https://api.twitter.com/2/users/{id}/tweets?max_results=100&tweet.fields=lang&exclude=retweets&pagination_token={pagination}&end_time=2022-09-15T00:00:00.000Z",headers=token).json()
        else:
            response = requests.get(f"https://api.twitter.com/2/users/{id}/tweets?max_results=100&tweet.fields=lang&exclude=retweets&pagination_token={pagination}",headers=token).json()
        return response
    except Exception as e:
        print(e)
        logger.error(f"Error in get_tweets function: {e}")
        logger.error(f"Error in get_tweets function: https://api.twitter.com/2/users/{id}/tweets?max_results=100&tweet.fields=lang&exclude=retweets:  {response}")
        if check_limits(response):
            token_selected = (token_selected+1)%(len(token_list))
            return get_tweets(id,pagination,token_list,token_selected,limit)

# Check if api responsed too many request
def check_limits(data):
    if data.get('title') is not None:
            if data['title'] == 'Too Many Requests' or data['title'] == 'UsageCapExceeded':
                print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!","limit error","!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!",time.localtime())
                duration = random.randint(0, 10)
                time.sleep(duration)
                return True
    return False


class CheckUser(APIView):
    def post(self, request, *args, **kwargs):
        token_list = [{"Authorization":"Bearer AAAAAAAAAAAAAAAAAAAAAJhGgQEAAAAANySENwDx71C%2F8M9p47UZNXr17vo%3DSNuMVMN3vDjcaYHYwnHVG9RxvVe5VnBDZJGVjJogivqaYfFpkt"}    
        ]
        username = request.POST.get('username')
        user = requests.get(f"https://api.twitter.com/2/users/by/username/{username}?user.fields=created_at,description,entities,id,location,name,pinned_tweet_id,profile_image_url,protected,public_metrics",headers=token_list[0]).json()
        if user.get("errors"):
            if user["errors"][0].get("title"):
                if user["errors"][0]["title"] == "Not Found Error":
                    return Response(-1)
            if user.get("title"):                    
                if user["title"] == "Invalid Request":
                    return Response(-1)
        elif user.get("data"):
            if user["data"].get("id"):
                if is_persian(user["data"]["id"],token_list,0):
                    return Response(1)
        print("finish!!!!!!!")
        return Response(0)
    
class SimpleCheckAndGetUser(APIView):
    def post(self, request, *args, **kwargs):
        token_list = [{"Authorization":"Bearer AAAAAAAAAAAAAAAAAAAAADJsggEAAAAAXm%2F5E119ZcawlGfoOukK6b%2F21uc%3D9K8dc0eGi19fCanaZMcUGMZj42La0aP3PVrka1I5YMQoDmBcvx"}    
        ]
        username = request.POST.get('username')
        print(username)
        user = requests.get(f"https://api.twitter.com/2/users/by/username/{username}?user.fields=created_at,description,entities,id,location,name,pinned_tweet_id,profile_image_url,protected,public_metrics",headers=token_list[0]).json()
        print(user)
        if user.get("errors"):
            if user["errors"][0].get("title"):
                if user["errors"][0]["title"] == "Not Found Error":
                    return Response({ 'username_check': -1})
            if user.get("title"):                    
                if user["title"] == "Invalid Request":
                    return Response({ 'username_check': -1})
        elif user.get("data"):
            if user["data"].get("id"):
                if user["data"]["public_metrics"]["tweet_count"] >= 300:
                    id = user["data"]["id"]
                    response1 = requests.get(f"https://api.twitter.com/2/users/{id}/tweets?max_results=100&tweet.fields=lang&exclude=retweets",headers=token_list[0]).json()
                    pagination1 = response1['meta']["next_token"]
                    response2 = requests.get(f"https://api.twitter.com/2/users/{id}/tweets?max_results=100&tweet.fields=lang&exclude=retweets&pagination_token={pagination1}",headers=token_list[0]).json()
                    pagination2 = response2['meta']["next_token"]
                    response3 = requests.get(f"https://api.twitter.com/2/users/{id}/tweets?max_results=100&tweet.fields=lang&exclude=retweets&pagination_token={pagination2}",headers=token_list[0]).json()
                    result = []
                    result += response1["data"]
                    result += response2["data"]
                    result += response3["data"]
                    tweets = []
                    for tweet in result:
                            tweets.append(tweet["text"])
                    print(tweets)
                    return Response({ 'username_check': 1 ,'twts': tweets})
                else:
                    return Response({ 'username_check': 0})

        return Response({ 'error': 'maybe token limited!'})


def is_persian(id,token_list,token_selected):
    try:
        token = token_list[token_selected]
        response = requests.get(f"https://api.twitter.com/2/users/{id}/tweets?max_results=100&tweet.fields=lang&exclude=retweets",headers=token).json()
        result = []
        print(response)
        result += response["data"]
        tweets = []
        n = 1
        while response['meta'].get("next_token") is not None and response['meta']['result_count'] > 0 and len(tweets) < 200 and n<4:
            if response['meta'].get("next_token") is not None:
                pagination = response['meta']["next_token"]
                response = get_tweets(id,pagination,token_list,token_selected,False)
                for tweet in result:
                    if tweet["lang"] == "fa":
                        tweets.append(tweet["text"])
                result += response["data"]
                n += 1
        print(len(tweets))
        if len(tweets) >= 200:
            return True
        else:
            return False



    except Exception as e:
        print(e)
        logger.error(f"Error in is_persian function:{e}")
        return False
            





class UserData(APIView):
    
    def post(self, request, *args, **kwargs):
        try:
            token_list = [{"Authorization":"Bearer AAAAAAAAAAAAAAAAAAAAAJhGgQEAAAAANySENwDx71C%2F8M9p47UZNXr17vo%3DSNuMVMN3vDjcaYHYwnHVG9RxvVe5VnBDZJGVjJogivqaYfFpkt"}    
            ]
            token_selected = 0
            token = token_list[token_selected]
            username = request.POST.get('username')
            user = requests.get(f"https://api.twitter.com/2/users/by/username/{username}?user.fields=created_at,description,entities,id,location,name,pinned_tweet_id,profile_image_url,protected,public_metrics",headers=token).json()
            id = user["data"]["id"]
            response = requests.get(f"https://api.twitter.com/2/users/{id}/tweets?max_results=100&tweet.fields=lang&exclude=retweets&end_time=2022-09-15T00:00:00.000Z",headers=token).json()
            result = []
            tweets = []
            if response.get("data"):
                result += response["data"]
                while response['meta'].get("next_token") is not None and response['meta']['result_count'] > 0 and len(tweets) < 200:
                    if response['meta'].get("next_token") is not None:
                        pagination = response['meta']["next_token"]
                        response = get_tweets(id,pagination,token_list,token_selected,True)
                        for tweet in result:
                            if tweet["lang"] == "fa":
                                tweets.append(tweet["text"])
                        result += response["data"]
            
            if len(tweets) >= 200:
                return Response({"tweets":tweets[0:200]})
            else:
                response2 = requests.get(f"https://api.twitter.com/2/users/{id}/tweets?max_results=100&tweet.fields=lang&exclude=retweets",headers=token).json()
                result2 = []
                result2 += response2["data"]
                tweets2 = []
                
                while response2['meta'].get("next_token") is not None and response2['meta']['result_count'] > 0 and len(tweets2) < 200:
                    if response2['meta'].get("next_token") is not None:
                        pagination2 = response2['meta']["next_token"]
                        response2 = get_tweets(id,pagination2,token_list,token_selected,False)
                        for tweet in result2:
                            if tweet["lang"] == "fa":
                                tweets2.append(tweet["text"])
                        result2 += response2["data"]
                
                return Response({"tweets":tweets2[0:200]})

        except Exception as e:
            print("error in get_details",e)
            print(token)
            logger.error(f"Error in get_details function: with token {token}")
            logger.error(f"Error in get_details function: {e}")
            logger.error(f"Error in get_details function: https://api.twitter.com/2/users/by/username/{username}?user.fields=created_at,description,entities,id,location,name,pinned_tweet_id,profile_image_url,protected,public_metrics:  {user}")
            if user.get("data") is not None:
                logger.error(f"Error in get_details function: https://api.twitter.com/2/users/{id}/tweets?max_results=100&tweet.fields=lang&exclude=retweets:  {response}")
                print(response)   
            print(user)
            return Response({"errors":e})




