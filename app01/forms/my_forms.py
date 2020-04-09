from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django import forms

from app01.models import UserInfo


class BaseModelForm(ModelForm):
    def __init__(self):
        super().__init__()
        for name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = '请输入%s' % field.label


class UserInfoModelForm(BaseModelForm):
    confirm_password = forms.CharField(label='确认密码', widget=forms.widgets.PasswordInput())
    password = forms.CharField(widget=forms.widgets.PasswordInput(), label='密码')
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

    def clean_mobile_phone(self):
        phone = self.cleaned_data.get('mobile_phone')
        obj = UserInfo.objects.filter(mobile_phone=phone).first()
        if obj:
            raise ValidationError('该用户存在')
        return phone


    # def clean_code(self):
    #     pass

    # def clean(self):
