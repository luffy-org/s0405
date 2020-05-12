from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse

from web.forms.wiki import WikiModelForm
from web.models import Wiki


def wiki(request, project_id):
    """wiki首页和wiki详细页的显示"""
    wiki_id = request.GET.get('wiki_id')
    if not wiki_id or not wiki_id.isdigit():
        return render(request, 'wiki.html')

    wiki_obj = Wiki.objects.filter(pk=wiki_id, project=project_id).first()
    return render(request, 'wiki.html', {'wiki_obj': wiki_obj})


def wiki_add(request, project_id):
    """添加wiki"""
    if request.method == 'GET':
        form = WikiModelForm(request)
        return render(request, 'wiki_add.html', {'forms': form})
    form = WikiModelForm(request, request.POST)

    if form.is_valid():
        if form.instance.parent:  # 如果选择了父wiki
            form.instance.depth = form.instance.parent.depth + 1  # 它的depth就应该是父wiki的depth+1
        else:
            form.instance.depth = 1
        form.instance.project = request.tracer.project  # 帮用户选择该wiki属于什么项目
        form.save()
        url = reverse('wiki', kwargs={'project_id': project_id})
        return redirect(url)
    return render(request, 'wiki_add.html', {'forms': form})


def wiki_order(request, project_id):
    """目录排序的ajax接口"""
    wiki_queryset = Wiki.objects.filter(project_id=project_id).order_by('depth', 'id').values('id', 'title', 'parent')
    data = list(wiki_queryset)
    return JsonResponse({'status': True, 'data': data})
