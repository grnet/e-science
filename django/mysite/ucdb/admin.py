from django.contrib import admin
from ucdb.models import UserInfo
from ucdb.models import UserLogin
from ucdb.models import ClusterInfo

# Register your models here.

admin.site.register(UserInfo)
admin.site.register(UserLogin)
admin.site.register(ClusterInfo)