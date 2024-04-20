from django.urls import path

from .views import  Delete, ExportNotAccepteddata, Exportdata, History, start_process



urlpatterns = [
    path('start/', start_process.as_view(), name='start_process'),
    path('history/', History.as_view(), name='history'),
    path('exportprocess/<int:id>/', Exportdata.as_view(), name='history'),
    path('exportnotaccepted/<int:id>/', ExportNotAccepteddata.as_view(), name='notacceptedprofiles'),
    path('delete/', Delete.as_view(), name='delete'),
]