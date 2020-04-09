from django.conf.urls import url



from app01 import views

urlpatterns = [
    url(r'^register/$', views.register),
    url(r'^api/send_msg/$', views.send_msg)
]
