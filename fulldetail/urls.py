from django.urls import path

from .views import DeleteProcess, Export_Parquets, Export_Pictures, FullData, History, UpdateData,GetTemplate



urlpatterns = [
    path('getexcel/', FullData.as_view(), name='getexcel'),
    path('exportparquets/<int:id>/', Export_Parquets.as_view(), name='exportparquets'),
    path('exportpictures/<int:id>/', Export_Pictures.as_view(), name='exportpictures'),
    path('update/<int:id>/', UpdateData.as_view(), name='updateexcel'),
    path('history/',History.as_view(), name= "history"),
    path('gettemplate/',GetTemplate.as_view(), name= "gettemplate"),
    path('deleteprocess/', DeleteProcess.as_view(), name='deleteprocess')
]