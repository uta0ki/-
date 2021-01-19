from django.contrib import admin
from .models import UserInfo, UserType, ClassInfo, Attendence, Leave

class UserInfoAdmin(admin.ModelAdmin):
    list_display = ['employeeNum', 'username', 'nickname', 'cid',
                    'password',
                    'gender', 'age', 'phone', 'email', 'motto'
                    ]


class UserTypeAdmin(admin.ModelAdmin):
    list_display = ['id', 'caption']


class ClassInfoAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']


class MajorInfoAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', ]


class AttendenceAdmin(admin.ModelAdmin):
    list_display = ['id', 'stu', 'date', 'start_time', 'end_time', 'is_leave', 'duration', 'detail']


class LeaveAdmin(admin.ModelAdmin):
    list_display = ['id', 'start_time', 'end_time', 'explain']


admin.site.register(UserType, UserTypeAdmin)
admin.site.register(UserInfo, UserInfoAdmin)
admin.site.register(ClassInfo, ClassInfoAdmin)
admin.site.register(Attendence, AttendenceAdmin)
admin.site.register(Leave, LeaveAdmin)

