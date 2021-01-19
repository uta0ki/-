"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url,include
from django.contrib import admin
from  app import views
urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$',views.index),
    url(r'^login/',views.login,name='login'),
    url(r'^register/',views.register,name='register'),
    url(r'^register_verify/',views.register_verify),
    url(r'^index/',views.index),
    url(r'^logout/',views.logout),
    url(r'^check/',views.check),
    url(r'^delete_check/',views.delete_check),
    url(r'^edit_check/',views.edit_check),
    url(r'^classManage/',views.classManage),
    url(r'^edit_class',views.edit_class),
    url(r'^delete_class',views.delete_class),
    url(r'^add_class/',views.add_class),
    url(r'^memberManage/',views.member_manage),
    url(r'^wageManage/',views.wage_manage),
    url(r'^delete_wage',views.delete_wage),
    url(r'^delete_member',views.delete_member),
    url(r'^edit_member',views.edit_member),
    url(r'^edit_wage',views.edit_wage),
    url(r'^total',views.total),
    url(r'^sign_solve/',views.total),
    url(r'^leave/',views.leave),
    url(r'^edit_leave/',views.elit_leave),
]
