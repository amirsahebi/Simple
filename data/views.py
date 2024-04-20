from concurrent.futures import process
import logging
from select import select
import time
import datetime
from .models import Process, Profile , NotAcceptedProfile
from django.shortcuts import render
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
import random
import xlwt
from django.http import HttpResponse
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from asgiref.sync import sync_to_async
from rest_framework.permissions import IsAuthenticated
from django.utils.decorators import classonlymethod
import asyncio
from tokenmanager.models import Token
logger = logging.getLogger('general')
# Create your views here.

# The main class that tokens define here then use functions to gather data
class start_process(APIView):
    # permission_classes = (IsAuthenticated,)
    def post(self, request, *args, **kwargs):
        print("OOOOKKKK")
        username = request.POST.get('username')
        description = request.POST.get('description')
        n = int(request.POST.get('count'))
        max_count = int(request.POST.get('max_count'))
        tokens = requests.post("http://65.108.150.18:6500/tokenlist/").json()
        token_list = []
        tokens = Token.objects.filter(active = True,active_labeling = True)
        print(tokens)
        token_list = []
        for token in tokens:
            token_list.append({"Authorization":f"Bearer {token.tokenaddress}"})
        token_selected = 0
        is_started = start(username,n,token_list,token_selected,max_count,description)
        return Response({"is_started":is_started})

# The start function that creates the starter node then call add function for rest of processes
def start(username,n,token_list,token_selected,max_count,description):
    try:
        token = token_list[token_selected]
        user = requests.get(f"https://api.twitter.com/2/users/by/username/{username}?user.fields=public_metrics",headers=token).json()
        id = user["data"]["id"]
        first = Profile.objects.create(accountaddress = username)

        list1=[({
            "id": f"{id}",
            "username": user["data"]["username"]
        },first)]
        if n>0:
            response = add(list1,n,token_list,token_selected,max_count,description)
        return response
    except Exception as e:
        logger.error(f"Error in start function: https://api.twitter.com/2/users/by/username/{username}?user.fields=public_metrics:  {user}")
        print(e)
        logger.error(f"Error in start function:{e}")
        if check_limits(user):
            token_selected = (token_selected+1)%(len(token_list))
            return start(username,n,token_list,token_selected,max_count,description)
        elif check_authorization(user):
            return False


# Convert data from database to excel and send it as file as a response file to client
class Exportdata(APIView):
    def get(self, request, *args, **kwargs):
        process = Process.objects.get(id = self.kwargs["id"])
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = f'attachment; filename="{process.created_at} GET_USERS.xls"'

        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('Users')

        # Sheet header, first row
        row_num = 0

        font_style = xlwt.XFStyle()
        font_style.font.bold = True

        columns = ['user','parent','created_at']

        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], font_style)

        # Sheet body, remaining rows
        font_style = xlwt.XFStyle()

        rows = Profile.objects.filter(processfield__pk = self.kwargs["id"]).values_list('accountaddress','parent__accountaddress','created_at')
        rows = [[x.strftime("%Y-%m-%d %H:%M") if isinstance(x, datetime.datetime) else x for x in row] for row in rows ]
        for row in rows:
            row_num += 1
            for col_num in range(len(row)):
                ws.write(row_num, col_num, row[col_num], font_style)

        wb.save(response)
        return response


class ExportNotAccepteddata(APIView):
    def get(self, request, *args, **kwargs):
        process = Process.objects.get(id = self.kwargs["id"])
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = f'attachment; filename="{process.created_at} GET_USERS.xls"'

        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('Users')

        # Sheet header, first row
        row_num = 0

        font_style = xlwt.XFStyle()
        font_style.font.bold = True

        columns = ['user','parent','created_at']

        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], font_style)

        # Sheet body, remaining rows
        font_style = xlwt.XFStyle()

        rows = NotAcceptedProfile.objects.filter(processfield__pk = self.kwargs["id"]).values_list('accountaddress','created_at')
        rows = [[x.strftime("%Y-%m-%d %H:%M") if isinstance(x, datetime.datetime) else x for x in row] for row in rows ]
        for row in rows:
            row_num += 1
            for col_num in range(len(row)):
                ws.write(row_num, col_num, row[col_num], font_style)

        wb.save(response)
        return response




# Get followings of one account and return it as list
def get_followings(id,token_list,token_selected,max_count):
    try:
        print("max_count:",max_count)
        if max_count<50:
            max_count = 50
        if max_count>500:
            max_count = 500
        print("max_count:",max_count)
        token = token_list[token_selected]
        response = requests.get(f"https://api.twitter.com/2/users/{id}/following?max_results={max_count}",headers=token).json()
        print(len(response['data']))
        result = []
        result += response["data"]
        # if followings_count > 1000:
        #     for _ in range(followings_count//1000):
        #         pagination = response['meta']["next_token"]
        #         response = requests.get(f"https://api.twitter.com/2/users/{id}/following?max_results=1000&pagination_token={pagination}",headers=token).json()
        #         result += response["data"]

        return result

    except Exception as e:
        try:
            logger.error(f"Error in get_followings function: https://api.twitter.com/2/users/{id}/following?max_results=1000:  {response}")
            # if response.get('meta'):
            #     if response['meta'].get("next_token") is not None:
            #         logger.error(f"Error in get_followings function: https://api.twitter.com/2/users/{id}/following?max_results=1000&pagination_token={pagination}:   {response}")
            print(e)
            logger.error(f"Error in get_followings function:{e}")
            if check_limits(response):
                token_selected = (token_selected+1)%(len(token_list))
                return get_followings(id,token_list,token_selected,max_count)
            elif check_authorization(response):
                return []
        except Exception as e:
            print(e)
            logger.error(f"Error in get_followings function:{e}")
            return []




class History(APIView):
    def get(self, request, *args, **kwargs):
        all_processes =  Process.objects.filter(is_open = False).order_by("-id")
        data = []
        if len(all_processes) > 0:
            for process in all_processes:
                if process.duration == 0:
                    sapm = process.succces_count
                else:
                    sapm = int(process.succces_count / process.duration)
                data.append({
                    "id":process.id,
                    "created_at":process.created_at,
                    "starting_node":process.starting_node.accountaddress,
                    "count":process.count,
                    "description":process.description,
                    "duration":process.duration,
                    "max_count":process.max_result,
                    "percentage":process.percentage,
                    "sapm": sapm,
                    "success_count": process.succces_count,
                    "reviewed_count": process.reviewed_count,
                    "success_percent":process.succces_percent,
                    "export_url":f"https://new.amir1380.tk/getuser/exportprocess/{process.id}/",
                    "notacceptedprofiles":f"https://new.amir1380.tk/getuser/exportnotaccepted/{process.id}/"
                }
                )
        else:
            data = False
        
        return Response({"processes":data})

        
       
       

        




# Check if the account has 100 tweets at list and check if it has at list 5 perisan tweet
def is_persian(id,token_list,token_selected):
    try:
        if NotAcceptedProfile.objects.filter(accountid = id):
            return [False,token_selected]
        token = token_list[token_selected]
        user = requests.get(f"https://api.twitter.com/2/users/{id}/tweets?max_results=10&tweet.fields=lang&exclude=retweets",headers=token).json()
        check = 0
        print(user["meta"]["result_count"])
        if user["meta"]["result_count"] == 10:
            for tweet in user["data"]:
                if tweet["lang"] == "fa":
                    check += 1
                if check >= 5:
                    print(True)
                    print("check:",check)
                    return [True,token_selected]
        print("check:",check)
        print(False)
        return [False,token_selected]
    except Exception as e:
        try:
            print(e)
            logger.error(f"Error in is_persian function: https://api.twitter.com/2/users/{id}/tweets?max_results=100&tweet.fields=lang&exclude=retweets: {user}")
            logger.error(f"Error in is_persian function:{e}")
            if check_limits(user):
                token_selected = (token_selected+1)%(len(token_list))
                return is_persian(id,token_list,token_selected)
            elif check_authorization(user):
                return [False,token_selected]
            else:
                return [False,token_selected]
        except Exception as e:
            print(e)
            logger.error(f"Error in is_persian function:{e}")
            return [False,token_selected]



        
# Most important function that create proccesses and use is_persian function for checking and get_followings to gather all data that we want
def add(list1,n,token_list,token_selected,max_count,description):
    try:
        token_selected = 0
        layer = get_channel_layer()
        starting_node = list1[0][1].accountaddress
        start_time = datetime.datetime.now()
        print("max_count:",max_count)
        print("description:",description)
        process1 = Process.objects.create(is_open = True,count=n,reviewed_count = 0,created_at = start_time.strftime("%m/%d/%Y, %H:%M:%S"),starting_node = list1[0][1],max_result = max_count,description = description)
        percent = 0
        success_percent = 0
        async_to_sync(layer.group_send)("dashboard1", {"type": "send_count1", "percent": percent,"is_open":True,"created_at":start_time.strftime("%m/%d/%Y, %H:%M:%S"),"count":n,"id":process1.id,"starting_node":starting_node,"is_good":True,"description":description,"max_count":max_count,"success_percent":success_percent})
        count = n
        # create childs for first node
        if len(list1)== 1:
            node = list1[0]
            parent = Profile.objects.create(accountaddress = node[0]["username"],parent = node[1],processfield = process1)
            count -= 1
            percent = int(((n-count)/n)*100)
            async_to_sync(layer.group_send)("dashboard1", {"type": "send_count1", "percent": percent,"is_open":True,"created_at":start_time.strftime("%m/%d/%Y, %H:%M:%S"),"count":n,"id":process1.id,"starting_node":starting_node,"is_good":True,"description":description,"max_count":max_count,"success_percent":success_percent})
            process1.percentage = percent
            process1.save()
            if count == 0:
                async_to_sync(layer.group_send)("dashboard1", {"type": "send_count1", "percent": percent,"is_open":False,"created_at":start_time.strftime("%m/%d/%Y, %H:%M:%S"),"count":n,"id":process1.id,"starting_node":starting_node,"is_good":True,"description":description,"max_count":max_count,"success_percent":success_percent})
                end_time = datetime.datetime.now()
                process1.duration = ((end_time-start_time).seconds)//60
                process1.is_open = False
                process1.save()
                return "finish"
            followings = get_followings(node[0]["id"],token_list,token_selected,max_count)
            for following in followings:
                list1.append((following,parent))
            list1.remove(node)
        i = 0
        reviewed_count = 1
        success_count = 1
        while i != len(list1):
            i += 1
            reviewed_count += 1
            node = list1[i]
            async_to_sync(layer.group_send)("dashboard1", {"type": "send_count1", "percent": percent,"is_open":True,"created_at":start_time.strftime("%m/%d/%Y, %H:%M:%S"),"count":n,"id":process1.id,"starting_node":starting_node,"is_good":True,"description":description,"max_count":max_count,"success_percent":success_percent})
            print(node)
            print(i,"-----------")
            print(len(list1))
            if i+2 >= len(list1):
                accepted = False
                print("11111111111111111111111111")
                while not accepted:
                    print("222222222222222222")
                    if not Profile.objects.filter(parent__accountaddress = list1[0][0]["username"]).exists():
                        if Profile.objects.filter(accountaddress = list1[0][0]["username"]).exists():
                            parent1 = Profile.objects.get(accountaddress = list1[0][0]["username"])
                            followings = get_followings(list1[0][0]["id"],token_list,token_selected,max_count)
                            if followings is not None:
                                if len(followings) > 1:
                                    for following in followings:
                                        list1.append((following,parent1))
                                    print(len(list1))
                                    accepted = True
                    list1.remove(list1[0])
                    i -= 1
            if not Profile.objects.filter(accountaddress = node[0]["username"]).exists():
                is_persian_data = is_persian(node[0]["id"],token_list,token_selected)
                if is_persian_data[0]:
                    token_selected = is_persian_data[1]
                    print(count)
                    parent = Profile.objects.create(accountaddress = node[0]["username"],parent = node[1],processfield = process1)
                    count -= 1
                    success_count += 1
                    print("n: ",n)
                    print("count: ",count)
                    print("((n-count)/n)*100: ",((n-count)/n)*100)
                    percent = int((((n-count)/n)*100) or 0)
                    async_to_sync(layer.group_send)("dashboard1", {"type": "send_count1", "percent": percent,"is_open":True,"created_at":start_time.strftime("%m/%d/%Y, %H:%M:%S"),"count":n,"id":process1.id,"starting_node":starting_node,"is_good":True,"description":description,"max_count":max_count,"success_percent":success_percent})
                    process1.percentage = percent
                    process1.succces_percent = (((n-count)/(i+1))*100)
                    process1.reviewed_count = reviewed_count
                    process1.succces_count = success_count
                    process1.save()
                    print(i,"+++++++++++")
                    print(len(list1))
                    if count == 0:
                        async_to_sync(layer.group_send)("dashboard1", {"type": "send_count1", "percent": percent,"is_open":False,"created_at":start_time.strftime("%m/%d/%Y, %H:%M:%S"),"count":n,"id":process1.id,"starting_node":starting_node,"is_good":True,"description":description,"max_count":max_count,"success_percent":success_percent})
                        end_time = datetime.datetime.now()
                        process1.duration = ((end_time-start_time).seconds)//60
                        process1.succces_percent = (((n-count)/(reviewed_count+1))*100)
                        process1.reviewed_count = reviewed_count
                        process1.succces_count = success_count
                        process1.is_open = False
                        process1.save()
                        return "finish"
                else:
                    NotAcceptedProfile.objects.create(accountaddress = node[0]["username"],accountid = node[0]["id"],processfield = process1)
    
        async_to_sync(layer.group_send)("dashboard1", {"type": "send_count1", "percent": percent,"is_open":False,"created_at":start_time.strftime("%m/%d/%Y, %H:%M:%S"),"count":n,"id":process1.id,"starting_node":starting_node,"is_good":False,"description":description,"max_count":max_count,"success_percent":success_percent})
        end_time = datetime.datetime.now()
        process1.duration = ((end_time-start_time).seconds)//60
        process1.succces_percent = (((n-count)/(i+1))*100)
        process1.reviewed_count = reviewed_count
        process1.succces_count = success_count
        process1.is_open = False
        process1.save()      
        return 0
    except Exception as e:
        logger.error(f"Error in add function:{e}")
        async_to_sync(layer.group_send)("dashboard1", {"type": "send_count1", "percent": percent,"is_open":False,"created_at":start_time.strftime("%m/%d/%Y, %H:%M:%S"),"count":n,"id":process1.id,"starting_node":starting_node,"is_good":False,"description":description,"max_count":max_count,"success_percent":success_percent})
        end_time = datetime.datetime.now()
        process1.duration = ((end_time-start_time).seconds)//60
        process1.succces_percent = (((n-count)/(i+1))*100)
        process1.reviewed_count = reviewed_count
        process1.succces_count = success_count
        process1.is_open = False
        process1.save()
        print(e)
    # except KeyError:
    #     print("555555555555555555555")
    #     username = list1[0][0]["username"]
    #     user = requests.get(f"https://api.twitter.com/2/users/by/username/{username}?user.fields=public_metrics",headers=token).json()
    #     id = user["data"]["id"]
    #     list1[0] = ({
    #         "id": f"{id}",
    #         "name": list1[0][0]["name"],
    #         "username": list1[0][0]["username"]
    #     },list1[0][1])
    #     add(list1,token,n)



# Check if api responsed too many request
def check_limits(data):
    if data.get('title') is not None:
            if data['title'] == 'Too Many Requests' or data['title'] == 'UsageCapExceeded':
                print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!","limit error","!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!",time.localtime())
                return True
    return False

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


# class Check_open_procces(View):
#     # permission_classes = (IsAuthenticated,)
#     @sync_to_async
#     def get(self, request, *args, **kwargs):
#         if len(Process.objects.filter(is_open=True)) == 0:
#             return HttpResponse({"is_open":False})
#         else:
#             return HttpResponse({"is_open":True})

class Delete(APIView):
    def post(self, request, *args, **kwargs):
        id = request.POST.get('id')
        print(id)
        token = Process.objects.get(id = id)

        token.delete()

        return Response({"deleted":True})


