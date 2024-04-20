from django.contrib import admin

from .models import Process, Profile

# Register your models here.

admin.site.register(Profile)
admin.site.register(Process)