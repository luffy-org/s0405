from django.conf.urls import url, include

from web.views import account, home, project, manage
urlpatterns = [
    url(r'^register/$', account.register, name='register'),
    url(r'^api/send_msg/$', account.send_msg),
    url(r'^sms/login/$', account.sem_login, name='sms_login'),
    url(r'^login/$', account.login, name='login'),
    url(r'^api/code/$', account.login_code, name='api_code'),
    url(r'^index/$', home.index, name='index'),
    url(r'^logout/$', account.logout, name='logout'),
    url(r'^project/list/$', project.list_project, name='list_project'),
    url(r'^project/star/(?P<project_type>\w+)/(?P<project_id>\d+)/$', project.project_star, name='project_star'),
    url(r'^project/unstar/(?P<project_type>\w+)/(?P<project_id>\d+)/$', project.project_unstar, name='project_unstar'),
    url(r'^manage/(?P<project_id>\d+)/', include([
        url(r'^dashboard/$', manage.dashboard, name='dashboard'),  # 项目详细页面
        url(r'^statistics/$', manage.statistics, name='statistics'),
        url(r'^issues/$', manage.issues, name='issues'),
        url(r'^setting/$', manage.setting, name='setting'),
        url(r'^file/$', manage.file, name='file'),
        url(r'^wiki/$', manage.wiki, name='wiki'),
    ], None, None))

]