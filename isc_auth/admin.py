from django.contrib import admin

# Register your models here.

from .models import Account,User,Application,Device

admin.site.register(Account)
admin.site.register(Application)
admin.site.register(User)
admin.site.register(Device)

