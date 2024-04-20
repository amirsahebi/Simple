from django.contrib import admin

from .models import Profile , Process, Reason


# Register your models here.

admin.site.register(Profile)
admin.site.register(Process)
admin.site.register(Reason)
