from django.conf.urls import url, include
from web.views import account, home, project, manage, wiki, file, settings

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
    # 项目功能
    url(r'^manage/(?P<project_id>\d+)/', include([
        url(r'^dashboard/$', manage.dashboard, name='dashboard'),  # 项目详细页面
        url(r'^statistics/$', manage.statistics, name='statistics'),
        url(r'^issues/$', manage.issues, name='issues'),
        url(r'^setting/$', settings.setting, name='setting'),
        url(r'^setting/delete/$', settings.setting_delete, name='setting_delete'),
        url(r'^wiki/$', wiki.wiki, name='wiki'),
        url(r'^wiki/add/$', wiki.wiki_add, name='wiki_add'),
        url(r'^wiki/edit/(?P<wiki_id>\d+)/$', wiki.wiki_edit, name='wiki_edit'),
        url(r'^wiki/delete/(?P<wiki_id>\d+)/$', wiki.wiki_delete, name='wiki_delete'),
        url(r'^wiki/order/$', wiki.wiki_order, name='wiki_order'),
        url(r'^wiki/upload/$', wiki.wiki_upload, name='wiki_upload'),
        url(r'^file/$', file.file, name='file'),
        url(r'^file/sts-cam/$', file.sts_cam, name='sts_cam'),
        url(r'^file/delete/$', file.file_delete, name='file_delete'),
        url(r'^file/file_add/$', file.file_add, name='file_add'),
        url(r'^file/download/(?P<file_id>\d+)/$', file.file_download, name='file_download')
    ], None, None))

]