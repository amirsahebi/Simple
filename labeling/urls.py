from tokenize import Token
from django.urls import path

from .views import AddProcess, AddReason, Chart, DeleteProcess, EnterLabeled, EnterReason, ExportInput, GetProfile, Processlist,Export, ReasonList



urlpatterns = [
    path('processlist/', Processlist.as_view(), name='processlist'),
    path('addprocess/', AddProcess.as_view(), name='addprocess'),
    path('getprofile/', GetProfile.as_view(), name='getprofile'),
    path('export/<int:id>/', Export.as_view(), name='export'),
    path('exportinput/<int:id>/', ExportInput.as_view(), name='exportinput'),
    path('enterlabeled/', EnterLabeled.as_view(), name='enterlabeled'),
    path('enterreason/', EnterReason.as_view(), name='enterreason'),
    path('addreason/', AddReason.as_view(), name='addreason'),
    path('reasonlist/', ReasonList.as_view(), name='reasonlist'),
    path('deleteprocess/', DeleteProcess.as_view(), name='deleteprocess'),
     path('chart/', Chart.as_view(), name='chart')
   
]