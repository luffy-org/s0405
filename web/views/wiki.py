from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse

from utils.Tencent.Cos import upload_file
from utils.encrypt import uid
from web.forms.wiki import WikiModelForm, WikiEditModelForm
from web.models import Wiki
from django.views.decorators.csrf import csrf_exempt


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


def wiki_edit(request, project_id, wiki_id):
    """编辑wiki"""
    wiki_obj = Wiki.objects.filter(pk=wiki_id, project=project_id).first()
    url = reverse('wiki', kwargs={'project_id': project_id})
    if not wiki_obj:
        return redirect(url)
    if request.method == 'GET':
        form = WikiEditModelForm(request, wiki_id, instance=wiki_obj)
        return render(request, 'wiki_add.html', {'forms': form})
    form = WikiEditModelForm(request, wiki_id, instance=wiki_obj, data=request.POST)
    if form.is_valid():
        if form.instance.parent:
            ret_depth = form.instance.parent.depth  # 拿到目标的depth
            my_depth = form.instance.depth  # 拿到原本的depth
            if my_depth > ret_depth:  # 我的层级比目标的多，所以
                form.instance.depth = ret_depth + 1
            elif my_depth < ret_depth:  # 我的层级比目标的少
                form.instance.depth = ret_depth - 1
        else:
            form.instance.depth = 1
        form.instance.project = request.tracer.project
        form.save()

        return redirect(url)

    return render(request, 'wiki_add.html', {'forms': form})


def wiki_delete(request, project_id, wiki_id):
    """删除wiki"""
    cancel = reverse('wiki', kwargs={'project_id': project_id})

    if request.method == 'GET':
        return render(request, 'wiki_delete.html', {'cancel': cancel})

    wiki_obj = Wiki.objects.filter(pk=wiki_id, project_id=project_id)
    wiki_obj.delete()
    return redirect(cancel)


@csrf_exempt
def wiki_upload(request, project_id):
    """wiki中上传文件"""

    img_obj = request.FILES.get('editormd-image-file')
    img_format = img_obj.name.rsplit('.')[-1]
    img_key = '{}.{}'.format(uid(request.tracer.user.mobile_phone), img_format)
    img_url = upload_file(
        bucket=request.tracer.project.bucket,  # 该项目的储存桶
        region=request.tracer.project.region,
        key=img_key,
        obj=img_obj
    )
    print('完成上传', img_url)
    result = {
        'success': 1,
        'message': None,
        'url': img_url

    }
    return JsonResponse(result)
