from web.forms.bootstrap import BootStrapForm
from django import forms

from web.models import Wiki


class WikiModelForm(BootStrapForm, forms.ModelForm):

    def __init__(self, request, *args, **kwargs):
        first_choice = [('', '-------')]
        super().__init__(*args, **kwargs)
        # self.request = request
        wiki_queryset = Wiki.objects.filter(project=request.tracer.project).values_list('id', 'title')
        first_choice.extend(wiki_queryset)
        self.fields['parent'].choices = first_choice

    class Meta:
        model = Wiki
        exclude = ['project', 'depth']


class WikiEditModelForm(BootStrapForm, forms.ModelForm):
    """编辑wiki的form"""

    def __init__(self, request, wiki_id, *args, **kwargs):
        first_choice = [('', '-------')]
        super().__init__(*args, **kwargs)
        wiki_queryset = Wiki.objects.filter(project=request.tracer.project).exclude(id=wiki_id).values_list('id',
                                                                                                            'title')
        first_choice.extend(wiki_queryset)
        self.fields['parent'].choices = first_choice

    class Meta:
        model = Wiki
        exclude = ['project', 'depth']
