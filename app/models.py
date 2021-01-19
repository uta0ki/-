from django.db import models
from django.utils import timezone


class UserType(models.Model):
    # 用户类型表  字段：用户类型
    caption = models.CharField(max_length=10)

    def __str__(self):
        return self.caption


class ClassInfo(models.Model):
    # 部门信息表  字段:部门名称
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name




class UserInfo(models.Model):
    # 创建用户模型，工号,密码，部门，姓名,昵称,用户类型,电话，姓名,座右铭,邮件,职位
    employeeNum = models.CharField(max_length=15, primary_key=True)
    password = models.CharField(max_length=64)
    username = models.CharField(max_length=15)
    cid = models.ForeignKey('ClassInfo', null=True, on_delete=models.CASCADE)
    nickname = models.CharField(max_length=30, null=True)
    hobby = models.CharField(max_length=30, null=True)
    age = models.IntegerField(null=True)
    user_type = models.ForeignKey(to='UserType', on_delete=models.CASCADE)
    gender = models.IntegerField(default=1)
    phone = models.CharField(max_length=11)
    motto = models.TextField(null=True)
    email = models.EmailField(null=False)
    position = models.CharField(max_length=80 ,null=True)
    salary = models.CharField(max_length=80, null=True)

    def __str__(self):
        return self.username

# 签到表设计
class Attendence(models.Model):
    #签到表   字段：用户，签到时间，签退时间，描述
    stu = models.ForeignKey('UserInfo', on_delete=models.CASCADE)
    # cur_time = models.DateTimeField(auto_now_add=True)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    duration = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    date = models.DateField(default=timezone.now)
    # state=models.BooleanField(default=False)
    is_leave = models.BooleanField(default=False)
    detail = models.TextField(default='无')
    leave_count = models.IntegerField(default=0)

    def __str__(self):
        return self.stu.username




# 请假表设计
class Leave(models.Model):
    # 请假表 字段：用户，开始时间，结束时间，请假原因
    user = models.ForeignKey(to='UserInfo', on_delete=models.CASCADE)
    start_time = models.DateField(null=True, blank=True)
    end_time = models.DateField(null=True, blank=True)
    explain = models.TextField(default='无', max_length=500)
    # 0:待审核 1：已通过 2：已拒绝
    state = models.CharField(max_length=30, null=True)

# 薪资表设计
class Wage(models.Model):
    emp = models.ForeignKey(to='UserInfo', on_delete=models.CASCADE)
    add_date = models.DateField(null=True, blank=True)
    wage = models.CharField(max_length=50)


