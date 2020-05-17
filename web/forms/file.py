from django import forms

from web.forms.bootstrap import BootStrapForm
from web.models import PorjectFile


class FileModelForm(BootStrapForm, forms.ModelForm):
    class Meta:
        model= PorjectFile
        fields = ['title']


