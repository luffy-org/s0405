import random

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.forms import ModelForm
from django import forms

from s0405 import settings
from utils.Tencent.sendSms import tencent_send_msg
from utils.encrypt import md5
from web.models import UserInfo
from django_redis import get_redis_connection


class BaseModelForm:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = '请输入%s' % field.label


class UserInfoModelForm(BaseModelForm, ModelForm):
    """
    验证注册
    """
    mobile_phone = forms.CharField(label='手机号',
                                   validators=[RegexValidator(r'^(1[3|4|5|6|7|8|9])\d{9}$', '手机号格式错误')])
    confirm_password = forms.CharField(label='确认密码', widget=forms.widgets.PasswordInput())
    password = forms.CharField(widget=forms.widgets.PasswordInput(), max_length=64, min_length=6,
                               error_messages={'max_length': '密码不能超过64位', 'min_length': '密码不能小于6位'}, label='密码')
    code = forms.CharField(label='验证码')

    class Meta:
        model = UserInfo
        fields = ['username', 'email', 'password', 'confirm_password', 'mobile_phone', 'code']

    def clean_username(self):
        name = self.cleaned_data.get('username')
        name_obj = UserInfo.objects.filter(username=name).first()
        if name_obj:
            raise ValidationError('该用户存在')
        return name

    def clean_email(self):
        email = self.cleaned_data.get('email')
        exist = UserInfo.objects.filter(email=email).exists()
        if exist:
            raise ValidationError('邮箱已存在')
        return email

    def clean_mobile_phone(self):
        phone = self.cleaned_data.get('mobile_phone')
        obj = UserInfo.objects.filter(mobile_phone=phone).first()
        if obj:
            raise ValidationError('该用户存在')
        return phone

    def clean_password(self):
        password = self.cleaned_data.get('password')
        return md5(password)

    def clean_confirm_password(self):
        pwd = self.cleaned_data.get('password')
        confirm_pwd = md5(self.cleaned_data.get('confirm_password'))
        if pwd != confirm_pwd:
            raise ValidationError('两次密码不一致')
        return confirm_pwd

    def clean_code(self):
        code = self.cleaned_data.get('code')  # 获取用户输入验证码
        conn = get_redis_connection('default')
        phone = self.cleaned_data.get('mobile_phone')
        if not phone:
            return code
        redis_code = conn.get(phone)

        if not redis_code:
            raise ValidationError('验证码失效，请重新获取验证码')
        if code.strip() != redis_code:
            raise ValidationError('验证码错误')
        return code


class SendSmsForm(forms.Form):
    """
    验证发送短信
    """

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

    mobile_phone = forms.CharField(label='手机号',
                                   validators=[RegexValidator(r'^(1[3|4|5|6|7|8|9])\d{9}$', '手机号格式错误')])

    def clean_mobile_phone(self):
        mobile_phone = self.cleaned_data.get('mobile_phone')  # 拿到通过格式校验的phone

        tpl = self.request.GET.get('tpl')
        template_id = settings.TENCENT_SMS_TEMPLATE.get(tpl)

        if not template_id:
            raise ValidationError('短信模版错误')
        exists = UserInfo.objects.filter(mobile_phone=mobile_phone).exists()
        if tpl == 'login':
            if not exists:
                raise ValidationError('手机号不存在')
        else:
            if exists:
                raise ValidationError('手机号已存在')

        code = str(random.randint(1000, 9999))
        sms = tencent_send_msg(mobile_phone, code, template_id)  # 发送验证码
        if sms:
            raise ValidationError('短信发送失败')
        conn = get_redis_connection("default")
        conn.set(mobile_phone, code, ex=60)

        return mobile_phone


class SmsLoginForm(BaseModelForm, forms.Form):
    """
    短信登陆
    """
    mobile_phone = forms.CharField(label='手机号',
                                   validators=[RegexValidator(r'^(1[3|4|5|6|7|8|9])\d{9}$', '手机号格式错误')])
    code = forms.CharField(label='验证码')

    def clean_mobile_phone(self):
        mobile_phone = self.cleaned_data.get('mobile_phone')
        user_obj = UserInfo.objects.filter(mobile_phone=mobile_phone).first()
        if not user_obj:
            raise ValidationError('手机号非法')
        return user_obj

    def clean_code(self):
        code = self.cleaned_data.get('code')
        user_obj = self.cleaned_data.get('mobile_phone')
        mobil_phone = user_obj.mobile_phone
        if not mobil_phone:
            return code
        conn = get_redis_connection('default')
        redis_code = conn.get(mobil_phone)
        if code.strip() != redis_code:
            raise ValidationError('验证码错误')
        return code



