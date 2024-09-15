from django.contrib import admin
from .views import CustomUser, UserProfile
# Register your models here.

admin.site.register(CustomUser)
admin.site.register(UserProfile)