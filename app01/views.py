from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

# Create your views here.
from django_redis import get_redis_connection

from app01.forms.my_forms import UserInfoModelForm
from utils.Tencent.sendSms import tencent_send_msg


def register(request):
    form = UserInfoModelForm()
    return render(request, 'register.html', {'form': form})


def send_msg(request):
    phone = request.GET.get('phone')
    tpl = request.GET.get('tpl')
    code = tencent_send_msg(phone)  # 生产的验证码
    print('验证码', code)

    """
    进行校验
    """


    data = {"msg":"恭喜你，完成ajax请求"}
    return JsonResponse(data)



