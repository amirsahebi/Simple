import logging
from django.http import FileResponse
import time
import datetime
from .models import Process,Profile, Reason
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
from django.db.models import Q
import numpy as np
from tokenmanager.models import Token

logger = logging.getLogger('general')

# Create your views here.

def import_data(impoted_file,pid):              
    try:  
        myfile = impoted_file       
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)
        excel_file = uploaded_file_url
        excel_file = urllib.parse.unquote(excel_file) 
        users = list(pd.read_excel("."+excel_file).user.dropna())
        age_low = list(pd.read_excel("."+excel_file).age_low)
        age_high = list(pd.read_excel("."+excel_file).age_high)
        gender = list(pd.read_excel("."+excel_file).gender)
        data = []
        for i in range(len(users)):
            data.append({'user':users[i],'age_low':age_low[i],'age_high':age_high[i],'gender':gender[i]})
        os.rename("."+excel_file,"."+f"/{pid}_LABELING.xlsx")
        return data
    except Exception as e:            
        print(e)
        logger.error(f"Error in import_data function:{e}")


def export_data(id):
    try:
        process = Process.objects.get(id = id)
        time = process.created_at

        
        columns = ['user','gender','age_low','age_high','tweet_count','bio','status','description']
        
        # If folder exist delete it
        if os.path.isfile(f"{time}_GET_LABELING.xlsx"):
            os.remove(f"{time}_GET_LABELING.xlsx")

        
        
        queryset = Profile.objects.filter(processfield = process, labeled = True).values_list('accountaddress','gender','age_low','age_high','tweet_count','bio','status','description')
        df = pd.DataFrame(list(queryset),columns=columns)

        df.to_excel(f"{time}_GET_LABELING.xlsx")


        print("time:",time)
        return time
    except Exception as e:
        print(e)
        print("error in export_data",e)
        logger.error(f"Error in export_data function: {e}")


# Export zip file as response to send it to client
class Export(APIView):
    def get(self, request, *args, **kwargs):
        time = export_data(self.kwargs["id"])
        return FileResponse(
            open(f"{time}_GET_LABELING.xlsx", 'rb'),
            as_attachment=True,
            filename=f'{time}_GET_LABELING.xlsx'
        )


class ExportInput(APIView):
    def get(self, request, *args, **kwargs):
        pid = self.kwargs["id"]
        return FileResponse(
            open(f"./{pid}_LABELING.xlsx", 'rb'),
            as_attachment=True,
            filename=f"{pid}_LABELING.xlsx"
        )

# Convet excel file to list and return it
class Processlist(APIView):
    def post(self, request, *args, **kwargs):
        processes = Process.objects.all().order_by("created_at")
        data = []
        
        for process in processes:
            wanted_percentage = (Profile.objects.filter(processfield = process,labeled = True).count() / Profile.objects.filter(processfield = process, labeled = False).count())*100
            low_age_percentage = ((Profile.objects.filter(processfield = process,labeled = True).count()+Profile.objects.filter(processfield = process,age_low__isnull = False, labeled = False).count())/ (Profile.objects.filter(processfield = process, labeled = False).count()+Profile.objects.filter(processfield = process, labeled = True).count()))*100
            high_age_percentage = ((Profile.objects.filter(processfield = process,labeled = True).count()+Profile.objects.filter(processfield = process,age_high__isnull = False, labeled = False).count())/ (Profile.objects.filter(processfield = process, labeled = False).count()+Profile.objects.filter(processfield = process, labeled = True).count()))*100
            gender_percentage = ((Profile.objects.filter(processfield = process, labeled = True).count()+Profile.objects.filter(Q(processfield = process) & ~Q(gender = "notselected") & Q(labeled = False)).count())/ (Profile.objects.filter(processfield = process, labeled = False).count()+Profile.objects.filter(processfield = process, labeled = True).count()))*100
            
            data.append({
                'id':process.id,
                'description':process.description,
                'count':process.count,
                'wanted_percentage':int(wanted_percentage),
                'low_age_percentage':int(low_age_percentage),
                'high_age_percentage':int(high_age_percentage),
                'gender_percentage':int(gender_percentage),
                'low_age_check':process.low_age_check,
                'high_age_check':process.high_age_check,
                'gender_check':process.gender_check,
                'excel_url':f"https://new.amir1380.tk/labeling/export/{process.id}/",
                'input_url':f"https://new.amir1380.tk/labeling/exportinput/{process.id}/",
                'created_at':process.created_at
            })
            
        return Response(data)

class DeleteProcess(APIView):
    def post(self, request, *args, **kwargs):
        id = request.POST.get('id')
        process = Process.objects.get(id = id)

        process.delete()

        return Response({"deleted":True})

class Chart(APIView):
    def get(self, request, *args, **kwargs):
        if Profile.objects.all():
            createds_date = [0]*30
            createds_count = [0]*30
            for i in range(0,30):
                createds_count[i] += Profile.objects.filter(modified_at__range=[(datetime.date.today()-datetime.timedelta(days=i)).strftime("%Y-%m-%d"),(datetime.date.today()-datetime.timedelta(days=i-1)).strftime("%Y-%m-%d")],labeled = True).count()
                createds_date[i] = int((datetime.date.today()-datetime.timedelta(days=i)).strftime("%d"))
        else:
            createds_date = [0]*30
            createds_count = [0]*30

        return Response({'createds_date':createds_date[::-1],'createds_count':createds_count[::-1]})

class AddProcess(APIView):
    def post(self, request, *args, **kwargs):
        try:
            description = request.POST.get('description')
            myfile = request.FILES['excel_file']
            process = Process.objects.create(description=description,created_at = datetime.datetime.now().strftime("%m\%d\%Y, %H:%M:%S"))
            profiles = import_data(myfile,process.id)
            print(profiles)
            flag = 0
            for profile in profiles:
                if not(profile['gender'] == 'male' or profile['gender'] == 'female'):
                    profile['gender'] = 'notselected'
                nlabeled = Profile.objects.create(accountaddress=profile['user'],gender = profile['gender'],processfield = process,flag = flag)

                if np.isnan(profile['age_low']) == False:
                    nlabeled.age_low = int(profile['age_low'])
                if np.isnan(profile['age_high']) == False:
                    nlabeled.age_high = int(profile['age_high'])
                nlabeled.save()
                flag += 1
                
                
            process.count = len(profiles)
            process.save()
            return Response({"success":True})

        except Exception as e:
            print(e)
            return Response({"success":False})
        
             

class GetProfile(APIView):
    def post(self, request, *args, **kwargs):
        print("Starteddddddddddd")
        tokens = Token.objects.filter(active = True,active_labeling = True)
        print(tokens)
        token_list = []
        for token in tokens:
            token_list.append({"Authorization":f"Bearer {token.tokenaddress}"})

        id = request.POST.get('id')
        direction = request.POST.get('direction')
        process = Process.objects.get(id = id)
        obj = Profile.objects.get(processfield = process, flag = process.flag)
        print(process.flag)

        print(token_list)
        
        if process.flag == 0:
            if direction == "next":
                obj = Profile.objects.get(processfield = process, flag = 1)
                process.flag += 1 
            elif direction == "back":
                obj = Profile.objects.get(processfield = process, flag = 0)
        elif process.flag >= len(Profile.objects.filter(processfield = process)) - 1:
            if direction == "back":
                obj = Profile.objects.get(processfield = process, flag = process.flag - 1)
                process.flag -= 1
            elif direction == "next":
                obj = Profile.objects.get(processfield = process, flag = process.flag)
        elif direction == "next":
            obj = Profile.objects.get(processfield = process, flag = process.flag + 1)
            process.flag += 1 
        elif direction == "back":
            obj = Profile.objects.get(processfield = process, flag = process.flag - 1)
            process.flag -= 1



            
            

            
        process.save()

        token_selected = 0
        
        
        profile_details = get_profile_details(obj.accountaddress,token_list,token_selected)
        
        print(profile_details)
        return Response({'person_id': obj.id,"embed":profile_details["embed"],"gender":obj.gender,"user":obj.accountaddress,"age_low":obj.age_low,"age_high":obj.age_high,"tweets_count":profile_details["tweets_count"],"bio":profile_details["bio"],"image":profile_details["image"]})

def get_profile_details(accountaddress,token_list,token_selected):
    try:
        token = token_list[token_selected]
        twitter_details = requests.get(f"https://api.twitter.com/1.1/users/show.json?screen_name={accountaddress}",headers=token).json()
        print(twitter_details)
        response = requests.get(f"https://publish.twitter.com/oembed?url=https%3A%2F%2Ftwitter.com%2F{accountaddress}")
        html_response =response.json()['html']
        image = (twitter_details["profile_image_url"]).replace("_normal","")

        return {"embed":html_response,"tweets_count":twitter_details["statuses_count"],"bio":twitter_details["description"],"image":image}
    
    except Exception as e:
        try:
            print("error in get_profile_details",e)
            print(token)
            logger.error(f"Error in get_profile_details function: with token {token}")
            logger.error(f"Error in get_profile_details function: {e}")
            logger.error(f"Error in get_profile_details function: https://api.twitter.com/1.1/users/show.json?screen_name={accountaddress}:  {twitter_details}")
            logger.error(f"Error in get_details function: https://publish.twitter.com/oembed?url=https%3A%2F%2Ftwitter.com%2F{accountaddress}:  {html_response}")
                
            if check_limits(twitter_details):
                print("user1",token_selected)
                token_selected = (token_selected+1)%(len(token_list))
                print("user2",token_selected)
                return get_profile_details(accountaddress,token_list,token_selected)
            elif check_authorization(twitter_details):
                return {"token_selected":token_selected}
            elif check_limits(response):
                print("response1",token_selected)
                token_selected = (token_selected+1)%(len(token_list))
                print("response2",token_selected)
                return get_profile_details(accountaddress,token_list,token_selected)
            elif check_authorization(response):
                return {"token_selected":token_selected}
            else:
                return {"token_selected":token_selected}
        except Exception as e1:
            print(e1)
            logger.error(f"Error in get_profile_details function: {e}")
            return {"embed":"","tweets_count":"","bio":"حساب وجود ندارد یا قابل بررسی نیست!","image":""}


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


# Check if api responsed too many request
def check_limits(data):
    if data.get('title') is not None:
            if data['title'] == 'Too Many Requests' or data['title'] == 'UsageCapExceeded':
                print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!","limit error","!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!",time.localtime())
                duration = random.randint(0, 10)
                time.sleep(duration)
                return True
    return False



class EnterLabeled(APIView):
    def post(self, request, *args, **kwargs):
        process_id = int(request.POST.get('process_id'))
        nonlabeled_id = int(request.POST.get('nonlabeled_id'))
        age_low = request.POST.get('age_low')
        age_high = request.POST.get('age_high')
        gender = request.POST.get('gender')
        description = request.POST.get('description')
        tweet_count = request.POST.get('tweet_count')
        bio = request.POST.get('bio')

            
        nonlabeled = Profile.objects.get(id = nonlabeled_id)
        if type(age_low) == int:
            nonlabeled.age_low = age_low
        if type(age_high) == int:
            nonlabeled.age_high = age_high
        if gender is not None:
            nonlabeled.gender = gender
        if description is not None:
            nonlabeled.description = description
        nonlabeled.status = "ok"
        nonlabeled.labeled = True
        nonlabeled.tweet_count = tweet_count
        nonlabeled.modified_at = datetime.datetime.now()
        nonlabeled.bio = bio
        nonlabeled.save()


        return Response({"labeled":nonlabeled.id})

class EnterReason(APIView):
    def post(self, request, *args, **kwargs):
        nonlabeled_id = int(request.POST.get('nonlabeled_id'))
        reason = request.POST.get('reason')
        

    
        nonlabeled = Profile.objects.get(id = nonlabeled_id)
        nonlabeled.labeled = True
        nonlabeled.description = reason
        nonlabeled.modified_at = datetime.datetime.now()
        nonlabeled.status = "not ok"
        nonlabeled.save()

        return Response({"labeled":nonlabeled.id})

class DeleteLastLabeled(APIView):
    def post(self, request, *args, **kwargs):
        
        id = int(request.POST.get('id'))
        labeled = Profile.objects.filter(processfield__id = id,labeled = True).last()
        labeled.delete()



class AddReason(APIView):
    def post(self, request, *args, **kwargs):
        
        reason = request.POST.get('reason')
        print(reason)
        reason = Reason.objects.create(reason = reason)
        return Response({"id":reason.id})

class ReasonList(APIView):
    def get(self, request, *args, **kwargs):
        reasons = Reason.objects.all()
        reason_list = []
        for reason in reasons:
            reason_list.append({"reason":reason.reason})
        return Response(reason_list)





        
            







        






