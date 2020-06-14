from django import forms
from django.forms import widgets as ws
from django.core.exceptions import ValidationError
from web.forms.bootstrap import BootStrapForm
from web.models import Issues, IssuesType, IssuesModel, ProjectUser, IssuesReply, ProjectInvite


class IssuseModelForm(BootStrapForm, forms.ModelForm):
    """问题ModelForm"""

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

        # 1. 筛选出该项目对应的问题类型
        self.fields['issues_type'].choices = IssuesType.objects.filter(project=self.request.tracer.project).values_list(
            'id', 'name')

        # 2.筛选出该问题对应的问题模块
        mode_list = [('', '--------')]
        mode_object_list = IssuesModel.objects.filter(project=self.request.tracer.project).values_list('id', 'name')
        mode_list.extend(mode_object_list)
        self.fields['issues_model'].choices = mode_list

        # 3. 该问题的指派、关注者只能是这个项目的参与者
        assign_attention_list = [('', '--------'), ]
        assign_attention_object_list = ProjectUser.objects.filter(project=self.request.tracer.project).values_list(
            'user__id', 'user__username')
        assign_attention_list.extend(assign_attention_object_list)
        self.fields['assign'].choices = assign_attention_list
        self.fields['attention'].choices = assign_attention_object_list

        # 4. 筛选出该项目下的所有问题
        parent_list = [('', '--------'), ]
        parent_object_list = Issues.objects.filter(project=request.tracer.project).values_list('id', 'title')
        parent_list.extend(parent_object_list)
        self.fields['parent'].choices = parent_list

    class Meta:
        model = Issues
        exclude = ['project', 'creator', 'create_datetime', 'latest_update_datetime ']
        widgets = {
            'status': ws.Select(attrs={'class': 'selectpicker', 'data-live-search': 'true'}),
            'issues_type': ws.Select(attrs={'class': 'selectpicker', 'data-live-search': 'true'}),
            'issues_model': ws.Select(attrs={'class': 'selectpicker', 'data-live-search': 'true'}),
            'level': ws.Select(attrs={'class': 'selectpicker', 'data-live-search': 'true'}),
            'assign': ws.Select(attrs={'class': 'selectpicker', 'data-live-search': 'true'}),
            'mode': ws.Select(attrs={'class': 'selectpicker', 'data-live-search': 'true'}),
            'parent': ws.Select(attrs={'class': 'selectpicker', 'data-live-search': 'true'}),
            'attention': ws.SelectMultiple(attrs={'class': 'selectpicker',
                                                  'data-live-search': 'true',
                                                  'data-actions-box': 'true'
                                                  }
                                           ),
        }

    def clean_title(self):
        title = self.cleaned_data['title']  # 用户输入的标题
        existst = Issues.objects.filter(project=self.request.tracer.project, title=title).exists()
        if existst:
            raise ValidationError('问题名称不能重复')
        return title


class IssuesReplyModelForm(forms.ModelForm):
    """问题评论的ModelForm"""
    class Meta:
        model = IssuesReply
        fields = ['content', 'parent_reply']


class ProjectInviteModelForm(BootStrapForm, forms.ModelForm):
    """项目邀请码ModelForm"""
    class Meta:
        model = ProjectInvite
        fields = ['count', 'period']

