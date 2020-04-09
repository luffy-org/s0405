from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

# Create your views here.
from app01.forms.my_forms import UserInfoModelForm


def register(request):
    form = UserInfoModelForm()
    return render(request, 'register.html', {'form': form})


def send_msg(request):
    phone = request.GET.get('phone')
    tpl = request.GET.get('tpl')
    print('拿到的Phone', phone)
    print(tpl)
    data = {"msg":"恭喜你，完成ajax请求"}
    return JsonResponse(data)