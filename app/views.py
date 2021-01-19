from django.shortcuts import render, HttpResponse, redirect
from .forms import loginForm
from django.contrib.auth import authenticate, login
from .api import check_cookie, check_login, DecimalEncoder, get_all_class, get_all_type, is_login
from .models import UserType, UserInfo, ClassInfo, Attendence, Leave, Wage
# django自带加密解密库
from django.views.decorators.csrf import csrf_exempt
from django.db.models import F, Q, Avg, Sum, Max, Min, Count
from django.core.paginator import Paginator
import json
import hashlib
import json
import datetime
import pytz
import time

# 首页
def index(request):
    return redirect('/check/')

# 签到统计
@is_login
def total(request):
    (flag, user) = check_cookie(request)
    condition = request.GET.get('condition')
    page = request.GET.get('page')
    if page:
        page = int(page)
    else:
        page = 1
    next_page = None
    prev_page = None
    if request.method == 'POST':
        nowdate = datetime.datetime.now()
        weekDay = datetime.datetime.weekday(nowdate)
        firstDay = nowdate - datetime.timedelta(days=weekDay)
        lastDay = nowdate + datetime.timedelta(days=6 - weekDay)
        info_list = Attendence.objects.filter(date__gte=firstDay, date__lte=lastDay).values('stu', 'stu__username',
                                                                                            'stu__cid__name',
                                                                                            'leave_count') \
            .annotate(total_time=Sum('duration')).order_by()
        info_list = json.dumps(list(info_list), cls=DecimalEncoder)

        return HttpResponse(info_list)
    else:
        nowdate = datetime.datetime.now()
        weekDay = datetime.datetime.weekday(nowdate)
        firstDay = nowdate - datetime.timedelta(days=weekDay)
        lastDay = nowdate + datetime.timedelta(days=6 - weekDay)
        leave_list = Leave.objects.filter().values('user', 'start_time', 'end_time')
        info_list = None
        if condition:
            info_list = ClassInfo.objects.filter(name__contains=condition)
            info_list = Attendence.objects.filter(date__gte=firstDay, date__lte=lastDay,stu__employeeNum__contains=condition).values('stu', 'stu__username',
                                                                                                'stu__cid__name',
                                                                                                'leave_count') \
                .annotate(total_time=Sum('duration')).order_by()
        else:
            info_list = Attendence.objects.filter(date__gte=firstDay, date__lte=lastDay).values('stu', 'stu__username',
                                                                                                'stu__cid__name',
                                                                                                'leave_count') \
                .annotate(total_time=Sum('duration')).order_by()
        paginator = Paginator(info_list, 2)


        print(info_list)
        paginator = Paginator(info_list, 2)
        # 总页数
        page_num = paginator.num_pages
        # 某一页
        page_info_list = paginator.page(page)
        if page_info_list.has_next():
            next_page = page + 1
        else:
            next_page = page
        if page_info_list.has_previous():
            prev_page = page - 1
        else:
            prev_page = page
        return render(request, 'total.html',{ 'info_list': page_info_list,
                              'page_num': range(1, page_num + 1),
                              'curr_page': page,
                              'next_page': next_page,
                              'prev_page': prev_page})

# 登录页面
@csrf_exempt
def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        m1 = hashlib.sha1()
        m1.update(password.encode('utf8'))
        password = m1.hexdigest()
        print('密码:', password)
        if check_login(email, password):
            response = redirect('/index/')
            response.set_cookie('qwer', email, 3600)
            response.set_cookie('asdf', password, 3600)
            return response
            # return HttpResponse('登录成功')
        else:
            return render(request, 'page-login.html', {'error_msg': '账号或密码错误请重新输入'})
    else:
        (flag, rank) = check_cookie(request)
        print('flag', flag)
        if flag:
            return redirect('/index/')
        return render(request, 'page-login.html', {'error_msg': ''})


# 注册页面
@csrf_exempt
def register(request):
    if request.method == 'POST':
        if request.is_ajax():

            stu_num_v = request.POST.get('stu_num_verify')
            if UserInfo.objects.filter(employeeNum=stu_num_v):
                ret = {'valid': False}
            else:
                ret = {'valid': True}

            return HttpResponse(json.dumps(ret))

    else:
        return render(request, 'register.html')


def check(request):
    (flag, rank) = check_cookie(request)
    # print('flag', flag)
    user = rank
    if flag:
        if request.method == 'POST':
            sign_flag = request.POST.get('sign')
            print('sign_flag', type(sign_flag), sign_flag)
            if sign_flag == 'True':
                Attendence.objects.create(stu=user, start_time=datetime.datetime.now())
            elif sign_flag == 'False':
                cur_attendent = Attendence.objects.filter(stu=user, end_time=None)
                tmp_time = datetime.datetime.now()
                duration = round((tmp_time - cur_attendent.last().start_time).seconds / 3600, 1)

                cur_attendent.update(end_time=tmp_time, duration=duration)
            return HttpResponse(request, '操作成功')
        else:
            role = rank.user_type.caption
            # 查询上一个签到的状态
            pre_att = Attendence.objects.filter(stu=user).order_by('id').last()
            # print(pre_att.end_time)
            if pre_att:
                # 如果当前时间距上次签到时间超过六小时，并且上次签退时间等于签到时间
                if (datetime.datetime.now() - pre_att.start_time.replace(
                        tzinfo=None)).seconds / 3600 > 6 and pre_att.end_time == None:
                    # Attendence.objects.filter(stu=user, end_time=None).update(end_time=pre_att.start_time+datetime.timedelta(hours=2),duration=2,detail="自动签退")
                    pre_att.delete()
                    sign_flag = True

                elif (datetime.datetime.now() - pre_att.start_time.replace(
                        tzinfo=None)).seconds / 3600 < 6 and pre_att.end_time == None:
                    sign_flag = False
                else:
                    sign_flag = True
            else:
                sign_flag = True
            att_list = None
            if rank.user_type.caption == 'admin':
                att_list = Attendence.objects.all().order_by('-id')
            else:
                att_list = Attendence.objects.filter(stu__employeeNum=rank.employeeNum)
            return render(request, 'check.html', locals())
    return render(request, 'page-login.html', {'error_msg': ''})

# 考勤删除
def delete_check(request):
    (flag, rank) = check_cookie(request)
    print('flag', flag)
    if flag:
        if rank.user_type.caption == 'admin':
            delete_id = request.GET.get('delete_id')
            Attendence.objects.filter(id=delete_id).delete()
            return redirect('/check/')
        else:
            return render(request, 'class_manage_denied.html')
    else:
        return render(request, 'page-login.html', {'error_msg': ''})

#   考勤编辑
def edit_check(request):
    (flag, rank) = check_cookie(request)
    if flag:
        if rank.user_type.caption == 'admin':
            if request.method == 'POST':
                id = request.POST.get('id')
                start_time = request.POST.get('start_time')
                end_time = request.POST.get('end_time')
                edit_obj = Attendence.objects.filter(id=id)
                duration =getMinute(start_time,end_time)/60
                duration = ('%.1f' % duration)
                if edit_obj:
                    edit_obj.update(start_time=start_time, end_time=end_time, duration=duration)
                return redirect('/check/')
            else:
                edit_attendence_id = request.GET.get('id')
                if edit_attendence_id:
                    # 当前编辑的用户对象
                    edit_stu_obj = Attendence.objects.get(id=edit_attendence_id)
                return render(request, 'edit_check.html', locals())
        else:
            return render(request, 'member_manage_denied.html')
    else:
        return render(request, 'page-login.html', {'error_msg': ''})

def getMinute(day1, day2):
    time_array1 = time.strptime(day1, "%Y-%m-%d %H:%M")
    timestamp_day1 = int(time.mktime(time_array1))
    time_array2 = time.strptime(day2, "%Y-%m-%d %H:%M")
    timestamp_day2 = int(time.mktime(time_array2))
    result = (timestamp_day2 - timestamp_day1) // 60
    return result

# 注销登录
def logout(request):
    req = redirect('/login/')
    req.delete_cookie('asdf')
    req.delete_cookie('qwer')
    return req


# 注册验证
def register_verify(request):
    if request.method == 'POST':
        print('验证成功')
        username = request.POST.get('username')
        email = request.POST.get('email')
        stu_num = request.POST.get('stu_num')
        pwd = request.POST.get('password')
        m1 = hashlib.sha1()
        m1.update(pwd.encode('utf8'))
        pwd = m1.hexdigest()
        phone = request.POST.get('phone')
        a = UserInfo.objects.create(username=username, email=email, employeeNum=stu_num, password=pwd,
                                    phone=phone, user_type_id=2)

        a.save()
        return HttpResponse('OK')


# 部门管理
def classManage(request):
    (flag, rank) = check_cookie(request)
    print('flag', flag)
    if flag:
        if rank.user_type.caption == 'admin':
            page = request.GET.get('page')
            condition = request.GET.get('condition')
            if page:
                page = int(page)
            else:
                page = 1
            next_page = None
            prev_page = None
            class_list = None
            if condition:
                class_list = ClassInfo.objects.filter(name__contains=condition)
            else:
                class_list = ClassInfo.objects.all()
            paginator = Paginator(class_list, 2)
            # 总页数
            page_num = paginator.num_pages
            # 某一页
            page_class_list = paginator.page(page)
            if page_class_list.has_next():
                next_page = page + 1
            else:
                next_page = page
            if page_class_list.has_previous():
                prev_page = page - 1
            else:
                prev_page = page
            return render(request, 'classManage.html',
                          {
                              'class_list': page_class_list,
                              'page_num': range(1, page_num + 1),
                              'curr_page': page,
                              'next_page': next_page,
                              'prev_page': prev_page
                           }
                          )
        else:
            return render(request, 'class_manage_denied.html')
    else:
        return render(request, 'page-login.html', {'error_msg': ''})


# 编辑部门
@csrf_exempt
def edit_class(request):
    (flag, rank) = check_cookie(request)
    print('flag', flag)
    if flag:
        if rank.user_type.caption == 'admin':
            if request.method == 'POST':
                pre_edit_id = request.POST.get('edit_id')
                class_name = request.POST.get('edit_class_name')
                temp_flag = ClassInfo.objects.filter(name=class_name)
                print('pre_edit_id1', pre_edit_id)
                pre_obj = ClassInfo.objects.get(id=pre_edit_id)
                if not temp_flag and class_name:
                    pre_obj.name = class_name
                    pre_obj.save()
                return HttpResponse('部门修改成功')
            class_list = ClassInfo.objects.all()
            return render(request, 'classManage.html', {'class_list': class_list})
            # return HttpResponse('编辑部门')
        else:
            return render(request, 'class_manage_denied.html')
    else:
        return render(request, 'page-login.html', {'error_msg': ''})


# 添加部门
@csrf_exempt
def add_class(request):
    if request.method == 'POST':
        add_class_name = request.POST.get('add_class_name')
        flag = ClassInfo.objects.filter(name=add_class_name)
        if flag:
            pass
        else:
            if add_class_name:
                ClassInfo.objects.create(name=add_class_name).save()

        return HttpResponse('添加部门成功')


# 删除部门
def delete_class(request):
    (flag, rank) = check_cookie(request)
    print('flag', flag)
    if flag:
        if rank.user_type.caption == 'admin':
            # class_list=ClassInfo.objects.all()
            delete_id = request.GET.get('delete_id')
            ClassInfo.objects.filter(id=delete_id).delete()
            return redirect('/classManage/')
        else:
            return render(request, 'class_manage_denied.html')
    else:
        return render(request, 'page-login.html', {'error_msg': ''})


# 档案管理
def member_manage(request):
    (flag, rank) = check_cookie(request)
    if flag:
        page = request.GET.get('page')
        condition = request.GET.get('condition')
        if page:
            page = int(page)
        else:
            page = 1
        next_page = None
        prev_page = None
        member_list = None
        if rank.user_type.caption == 'admin':
            member_list = UserInfo.objects.all()
            if condition:
                member_list = UserInfo.objects.filter(employeeNum__contains=condition)
            else:
                member_list = UserInfo.objects.all()
        else:
            member_list = UserInfo.objects.filter(employeeNum=rank.employeeNum)
        paginator = Paginator(member_list, 2)
        # 总页数
        page_num = paginator.num_pages
        # 某一页
        page_member_list = paginator.page(page)
        if page_member_list.has_next():
            next_page = page + 1
        else:
            next_page = page
        if page_member_list.has_previous():
            prev_page = page - 1
        else:
            prev_page = page
        return render(request, 'member_manage.html',
                      {
                          'member_list': page_member_list,
                          'page_num': range(1, page_num + 1),
                          'curr_page': page,
                          'next_page': next_page,
                          'prev_page': prev_page,
                          'role': rank.user_type.caption
                      }
                      )
    else:
        return render(request, 'page-login.html', {'error_msg': ''})


# 删除档案
def delete_member(request):
    (flag, rank) = check_cookie(request)
    if flag:
        if rank.user_type.caption == 'admin':
            delete_sno = request.GET.get('delete_sno')
            UserInfo.objects.get(employeeNum=delete_sno).delete()
            return redirect('/memberManage/')
        else:
            return render(request, 'member_manage_denied.html')
    else:
        return render(request, 'page-login.html', {'error_msg': ''})


#   编辑档案
def edit_member(request):
    (flag, rank) = check_cookie(request)
    if flag:
        if rank.user_type.caption == 'admin':

            if request.method == 'POST':
                student_num = request.POST.get('student_num')
                username = request.POST.get('username')
                email = request.POST.get('email')
                age = request.POST.get('age')
                if age:
                    age = int(age)
                else:
                    age = 0

                gender = int(request.POST.get('gender'))
                position = request.POST.get('position')
                salary = request.POST.get('salary')
                pwd = request.POST.get('pwd')
                m1 = hashlib.sha1()
                m1.update(pwd.encode('utf8'))
                pwd = m1.hexdigest()
                cls = ClassInfo.objects.get(name=request.POST.get('cls'))
                nickname = request.POST.get('nickname')
                usertype = UserType.objects.get(caption=request.POST.get('user_type'))
                phone = request.POST.get('phone')
                motto = request.POST.get('motto')
                edit_obj = UserInfo.objects.filter(employeeNum=student_num)
                if edit_obj:
                    edit_obj.update(employeeNum=student_num, username=username, email=email, cid=cls, nickname=nickname,
                                    user_type=usertype, motto=motto,
                                    gender=gender, phone=phone,
                                    age=age,
                                    position=position,
                                    salary=salary
                                    )
                else:
                    a = UserInfo.objects.create(employeeNum=student_num, username=username, email=email, cid=cls, nickname=nickname,
                                    user_type=usertype, motto=motto,
                                    gender=gender, phone=phone,
                                    age=age,
                                    position=position,
                                    salary=salary,
                                    password=pwd)
                    a.save()
                member_list = UserInfo.objects.all()
                return redirect('/memberManage/', {'member_list': member_list})
            else:
                edit_member_id = request.GET.get('edit_sno')
                # 所有用户类型列表
                stu_type_list = UserType.objects.all()
                # 所有的部门
                cls_list = ClassInfo.objects.all()
                if edit_member_id:
                    # 当前编辑的用户对象
                    edit_stu_obj = UserInfo.objects.get(employeeNum=edit_member_id)
                return render(request, 'edit_member.html', locals())
        else:
            return render(request, 'member_manage_denied.html')
    else:
        return render(request, 'page-login.html', {'error_msg': ''})

# 薪资管理
def wage_manage(request):
    (flag, rank) = check_cookie(request)
    if flag:
        page = request.GET.get('page')
        condition = request.GET.get('condition')
        if page:
            page = int(page)
        else:
            page = 1
        next_page = None
        prev_page = None
        wage_list = None
        if rank.user_type.caption == 'admin':
            wage_list = Wage.objects.all()
            if condition:
                wage_list = Wage.objects.filter(emp_employeeNum__contains=condition)
            else:
                wage_list = Wage.objects.all()
        else:
            wage_list = Wage.objects.filter(emp__employeeNum=rank.employeeNum)
        paginator = Paginator(wage_list, 2)
        # 总页数
        page_num = paginator.num_pages
        # 某一页
        page_wage_list = paginator.page(page)
        if page_wage_list.has_next():
            next_page = page + 1
        else:
            next_page = page
        if page_wage_list.has_previous():
            prev_page = page - 1
        else:
            prev_page = page
        return render(request, 'wage_manage.html',
                      {
                          'wage_list': page_wage_list,
                          'page_num': range(1, page_num + 1),
                          'curr_page': page,
                          'next_page': next_page,
                          'prev_page': prev_page,
                          'role': rank.user_type.caption
                      }
                      )
    else:
        return render(request, 'page-login.html', {'error_msg': ''})

#   编辑薪资
def edit_wage(request):
    (flag, rank) = check_cookie(request)
    if flag:
        if rank.user_type.caption == 'admin':
            if request.method == 'POST':
                wage = request.POST.get('wage')
                add_date = request.POST.get('add_date')
                add_date = add_date.replace('年', '-')
                add_date = add_date.replace('月', '-')
                add_date = add_date.replace('日', '')
                edit_id = request.POST.get('id')
                emp = UserInfo.objects.get(employeeNum=request.POST.get('emp'))
                if edit_id:
                    edit_obj = Wage.objects.filter(id=edit_id)
                    edit_obj.update(wage=wage,add_date=add_date,
                                    emp=emp
                                    )
                else:
                    a = Wage.objects.create(wage=wage,add_date=add_date,
                                    emp=emp)
                    a.save()
                return redirect('/wageManage/')
            else:
                edit_wage_id = request.GET.get('id')
                # 所有员工列表
                user_list = UserInfo.objects.all()
                if edit_wage_id:
                    # 当前编辑的对象
                    edit_wage_obj = Wage.objects.get(id=edit_wage_id)
                return render(request, 'edit_wage.html', locals())
        else:
            return render(request, 'member_manage_denied.html')
    else:
        return render(request, 'page-login.html', {'error_msg': ''})

# 删除薪资
def delete_wage(request):
    (flag, rank) = check_cookie(request)
    print('flag', flag)
    if flag:
        if rank.user_type.caption == 'admin':
            delete_id = request.GET.get('id')
            Wage.objects.filter(id=delete_id).delete()
            return redirect('/wageManage/')
        else:
            return render(request, 'class_manage_denied.html')
    else:
        return render(request, 'page-login.html', {'error_msg': ''})


# 请假管理
@is_login
def leave(request):
    (flag, user) = check_cookie(request)
    leave_list = None
    if user.user_type.caption == 'admin':
        leave_list = Leave.objects.all()
    else:
        leave_list = Leave.objects.filter(user_id = user.employeeNum)
    if request.method == 'POST':
        starttime = request.POST.get('starttime')
        endtime = request.POST.get('endtime')
        print(starttime)
        a = int(datetime.datetime.strptime(starttime, '%Y-%m-%d').day - datetime.datetime.strptime(endtime,
                                                                                                   '%Y-%m-%d').day) + 1
        explain = request.POST.get('explain')
        Leave.objects.create(start_time=starttime, end_time=endtime, user=user, explain=explain,state='0')
        Attendence.objects.filter(date__gte=starttime, date__lte=endtime, stu=user).update(
            leave_count=F('leave_count') + a)
    return render(request, 'leave.html', {"role": user.user_type.caption, "leave_list": leave_list}, locals())

# 修改请假状态
def elit_leave(request):
    (flag, rank) = check_cookie(request)
    print('flag', flag)
    if flag:
        if rank.user_type.caption == 'admin':
            state = request.GET.get('state')
            id = request.GET.get('id')
            edit_obj = Leave.objects.get(id=id)
            edit_obj.state = state
            edit_obj.save()
            return redirect('/leave/')
        else:
            return render(request, 'class_manage_denied.html')
    else:
        return render(request, 'page-login.html', {'error_msg': ''})
