from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse

from web.forms.wiki import WikiModelForm


def wiki(request, project_id):
    return render(request, 'wiki.html')


def wiki_add(request, project_id):
    """添加wiki"""
    if request.method == 'GET':
        form = WikiModelForm(request)
        return render(request, 'wiki_add.html', {'forms': form})
    form = WikiModelForm(request, request.POST)

    if form.is_valid():
        form.instance.project = request.tracer.project  # 帮用户选择该wiki属于什么项目
        form.save()
        url = reverse('wiki', kwargs={'project_id': project_id})
        return redirect(url)
    return render(request, 'wiki_add.html', {'forms': form})


def wiki_order(request, project_id):
    return JsonResponse({'status': True, 'data': 'data'})