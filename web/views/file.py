import json

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from s0405 import settings
from sts.sts import Sts

from web.forms.file import FileModelForm
from web.models import PorjectFile


def file(request, project_id):
    folder_id = request.GET.get('folder_id', '')
    if request.method == 'GET':

        menu_list = []
        if folder_id:
            folder_id = int(folder_id)
            ret_obj = PorjectFile.objects.filter(id=folder_id, file_type=1).first()
            form = FileModelForm(instance=ret_obj)
            while ret_obj:
                menu_list.insert(0, {'id': ret_obj.id, 'title': ret_obj.title})
                ret_obj = ret_obj.parent
            file_query_set = PorjectFile.objects.filter(project=project_id, parent=folder_id)
        else:
            form = FileModelForm()
            file_query_set = PorjectFile.objects.filter(project=project_id, parent=None)

        return render(request, 'file.html', {'file_query_set': file_query_set, 'menu_list': menu_list, 'forms': form, 'folder_id': folder_id})

    form = FileModelForm(data=request.POST)

    if form.is_valid():
        parent_id = request.POST.get('parent')
        form.instance.project = request.tracer.project
        form.instance.parent_id = parent_id
        form.instance.update_user = request.tracer.user
        form.save()
        print('完成创建')
        return JsonResponse({'status': True})
    print(form.errors)
    return JsonResponse({'status': False, 'errors': form.errors})


def file_post(request, project_id):
    return render(request, 'sts-post.html')


def sts_cam(request, project_id):
    config = {
        # 临时密钥有效时长，单位是秒
        'duration_seconds': 1800,
        'secret_id': settings.SecretId,
        'secret_key': settings.SecretKey,
        'bucket': request.tracer.project.bucket,
        'region': request.tracer.project.region,
        'allow_prefix': '*',
        # allow-actions: 权限
        'allow_actions': [
            # 简单上传
            'name/cos:PutObject',
            'name/cos:PostObject',
            # 分片上传
            'name/cos:InitiateMultipartUpload',
            'name/cos:ListMultipartUploads',
            'name/cos:ListParts',
            'name/cos:UploadPart',
            'name/cos:CompleteMultipartUpload'
        ]
    }
    sts = Sts(config)
    response = sts.get_credential()
    ret = json.dumps(dict(response), indent=4)
    print('得到临时密钥:' + ret)
    return JsonResponse(response)



def file_edit(request, project_id):
    """编辑文件夹"""
    folder_id = request.GET.get('folder_id', '')
    file_obj = PorjectFile.objects.filter(project=project_id, id=folder_id).first()
    form = FileModelForm(instance=file_obj)
