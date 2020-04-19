from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect

from io import BytesIO
from utils.pill import check_code
from web.forms.account import UserInfoModelForm, SendSmsForm, SmsLoginForm, LoginForm
from web.models import UserInfo


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
    form = SendSmsForm(request, data=request.GET)
    if form.is_valid():  # 完成对手机的校验,发送短信并写入redis
        data = {"status": True}
        return JsonResponse(data)

    return JsonResponse({"status": False, "error": form.errors})


def sem_login(request):
    """
    利用手机好进行登陆
    :param request:
    :return:
    """
    if request.method == 'GET':
        form = SmsLoginForm()
        return render(request, 'login_sms.html', {'form': form})

    form = SmsLoginForm(data=request.POST)

    if form.is_valid():
        return JsonResponse({"status": True, "data": "/index/"})
    return JsonResponse({"status": False, "error": form.errors})


def login(request):
    """
    账号登陆
    :param request:
    :return:
    """
    if request.method == 'GET':
        form = LoginForm(request)
        return render(request, 'login.html', {'form': form})
    form = LoginForm(request, data=request.POST)
    if form.is_valid():
        pwd = form.cleaned_data.get('pwd')
        user = form.cleaned_data.get('username')
        # user_obj = UserInfo.objects.filter(username=user, password=pwd).first()
        user_obj = UserInfo.objects.filter(Q(email=user,password=pwd)|Q(mobile_phone=user, password=pwd)).first()
        if  user_obj:
            request.session['user_id'] = user_obj.id
            return redirect('/index/')
        form.add_error('pwd', '用户名密码错误')
    return render(request, 'login.html', {'form': form})




def login_code(request):
    """
    或者账号登陆的验证码
    :param request:
    :return:
    """
    img_object, code = check_code()  # img图片对象  code验证码
    stream = BytesIO()
    img_object.save(stream, format='png')
    # 在生产验证码的同时，将验证码储存起来方便校验
    request.session['login_code'] = code  # 将生成的code储存到session中
    return HttpResponse(stream.getvalue())


def logout(request):
    request.session.flush()
    return redirect('/index/')