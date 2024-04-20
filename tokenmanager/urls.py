from tokenize import Token
from django.urls import path

from .views import Activate, AddToken, Deactivate, Delete, Tokenlist



urlpatterns = [
    path('tokenlist/', Tokenlist.as_view(), name='tokenlist'),
    path('addtoken/', AddToken.as_view(), name='addtoken'),
    path('activate/', Activate.as_view(), name='activate'),
    path('deactivate/', Deactivate.as_view(), name='deactivate'),
    path('delete/', Delete.as_view(), name='delete')
]