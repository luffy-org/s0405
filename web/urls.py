from django.conf.urls import url
from web.views import account, home
urlpatterns = [
    url(r'^register/$', account.register, name='register'),
    url(r'^api/send_msg/$', account.send_msg),
    url(r'^sms/login/$', account.sem_login, name='sms_login'),
    url(r'^login/$', account.login, name='login'),
    url(r'^api/code/$', account.login_code, name='api_code'),
    url(r'^index/$', home.index),
    url(r'^logout/$', account.logout, name='logout')
]