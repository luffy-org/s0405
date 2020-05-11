from django import forms
from django.core.exceptions import ValidationError
from web.forms.bootstrap import BootStrapForm
from web.forms.widget import ColorRadioSelect
from web.models import Project


class ProjectModelForm(BootStrapForm, forms.ModelForm):
    bootstrap_class_exclude = ['color']

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

    class Meta:
        model = Project
        fields = ['name', 'color', 'desc']
        widgets = {
            'desc': forms.Textarea,
            'color': ColorRadioSelect(attrs={'class': 'color-radio'})

        }

    def clean_name(self):
        """交易项目名称"""
        name = self.cleaned_data.get('name')  # 拿到用户提交的项目名称
        user_obj = self.request.tracer.user  # 拿到当前用户
        exists = Project.objects.filter(name=name, creator=user_obj).exists()
        # 1. 校验项目名称
        if exists:
            raise ValidationError('项目已存在')
        # 2. 校验当前用户是否还可以创建项目
        count = Project.objects.filter(creator=user_obj).count()
        user_price_policy = self.request.tracer.price_policy
        print('价格策略', user_price_policy.title)
        if count >= user_price_policy.project_length:
            raise ValidationError('项目个数已超过免费额度，免费额度只能创建3个项目')

        return name


