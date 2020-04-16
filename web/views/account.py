from django.http import JsonResponse, HttpResponse
from django.shortcuts import render

from utils.Tencent.sendSms import tencent_send_msg
from web.forms.account import UserInfoModelForm, SendSmsForm


def register(request):
    if request.method == 'GET':
        form = UserInfoModelForm()
        return render(request, 'register.html', {'form': form})
    print('前端通过ajax传递来的值', request.POST)
    form = UserInfoModelForm(data=request.POST)

    if form.is_valid():
        ret = form.save()  # 添加数据
        print('添加数据', ret)
        return JsonResponse({"status": True, "data": "/login/"})
    print(form.errors)
    return JsonResponse({"status": False, "error": form.errors})


def send_msg(request):
    """
    对手机号进行校验，通过后发送验证码
    :param request:
    :return:
    """
    form = SendSmsForm(data=request.GET)
    if form.is_valid():  # 完成对手机的校验,发送短信并写入redis
        data = {"status": True}
        return JsonResponse(data)
    print(form.errors)

    return JsonResponse({"status": False, "error": form.errors})


def sem_login(request):
    """
    利用手机好进行登陆
    :param request:
    :return:
    """
