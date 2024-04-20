from django.urls import path

from .views import CheckUser, UserData, SimpleCheckAndGetUser



urlpatterns = [
    path('check/', CheckUser.as_view(), name='checkuser'),
    path('getdata/', UserData.as_view(), name='userdata'),
    path('simpleget/', SimpleCheckAndGetUser.as_view(), name='SimpleCheckAndGetUser')
]