from django import forms
from django.core.exceptions import ValidationError
from web.forms.bootstrap import BootStrapForm
from web.models import PorjectFile


class FileModelForm(BootStrapForm, forms.ModelForm):
    class Meta:
        model = PorjectFile
        fields = ['title']

    def __init__(self, request, parent_obj, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        self.parent_obj = parent_obj

    def clean_title(self):
        file_name = self.cleaned_data.get('title')
        query = PorjectFile.objects.filter(project=self.request.tracer.project, title=file_name, file_type=1)
        if self.parent_obj:
            exists = query.filter(parent=self.parent_obj).exists()
        else:
            exists = query.filter(parent__isnull=True).exists()
        if exists:
            raise ValidationError('文件夹已存在')
        return file_name


class EditFileModelForm(BootStrapForm, forms.ModelForm):
    class Meta:
        model = PorjectFile
        fields = ['id', 'title']
