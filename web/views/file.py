import json

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from s0405 import settings
from sts.sts import Sts

from utils.Tencent.Cos import delete_object, delete_object_list
from web.forms.file import FileModelForm, EditFileModelForm
from web.models import PorjectFile


def file(request, project_id):
    folder_id = request.GET.get('folder_id', '')  # 获取父ID
    folder_obj = None
    if folder_id.isdecimal():  # 防止通过修改url参数
        folder_id = int(folder_id)
        folder_obj = PorjectFile.objects.filter(id=folder_id, project=request.tracer.project,
                                                file_type=1).first()  # 拿到父对象

    if request.method == 'GET':
        form = FileModelForm(request, folder_obj)
        update_forms = None
        menu_list = []
        parent = folder_obj
        while parent:
            menu_list.insert(0, {'id': parent.id, 'title': parent.title})
            parent = parent.parent

        file_query_set = PorjectFile.objects.filter(project=request.tracer.project, parent=folder_obj)

        context = {
            'file_query_set': file_query_set,
            'menu_list': menu_list,
            'forms': form,
            'update_forms': update_forms,
            'folder_id': folder_id
        }
        return render(request, 'file.html', context)

    fid = request.POST.get('fid', '')
    file_obj = None
    if fid.isdecimal():
        file_obj = PorjectFile.objects.filter(project=request.tracer.project, id=fid).first()
    if file_obj:
        form = FileModelForm(request, folder_obj, data=request.POST, instance=file_obj)
    else:
        form = FileModelForm(request, folder_obj, data=request.POST)

    if form.is_valid():
        form.instance.project = request.tracer.project
        form.instance.parent = folder_obj
        form.instance.update_user = request.tracer.user
        form.save()
        print('完成创建')
        return JsonResponse({'status': True})
    print(form.errors)
    return JsonResponse({'status': False, 'errors': form.errors})


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


def file_delete(request, project_id):
    """删除文件的ajax请求"""
    pid = request.GET.get('pid', '')
    ret_obj = request.tracer.project
    file_obj = PorjectFile.objects.filter(project=request.tracer.project, id=pid).first()


    if file_obj.file_type == 1:  # 如果是文件夹则需要循环删除文件夹内的所有文件
        total_size = 0
        delete_folder_list = [file_obj,]  # 目标文件夹
        delete_file_list = []  # 需要删除的文件，加入到列表里可以在cos中批量删除

        for folder in delete_folder_list:  # folder为文件夹
            query_list = PorjectFile.objects.filter(project=request.tracer.project, parent=folder).order_by('file_type')
            # 循环每个文件夹
            for item in query_list:
                if item.file_type == 1:
                    delete_folder_list.append(item)  # 如果是文件夹加入到文件夹列表循环进行判断

                else:  # 是文件， 就调用cos接口将其删除
                    total_size += item.file_capacity
                    delete_file_list.append({'Key': item.key})  # 将对象加入到删除列表里

        if delete_file_list: # 有需要删除的文件
            delete_object_list(ret_obj.bucket, delete_file_list)

        if total_size:
            ret_obj.use_space -= total_size
            ret_obj.save()

        file_obj.delete()
        return JsonResponse({'status': True})

    else:
        # 1. 恢复容量大小

        ret_obj.use_space -= file_obj.file_capacity  # 该项目的容量-该文件的容量
        ret_obj.save()
        delete_object(ret_obj.bucket, file_obj.key)  # cos中删除
        file_obj.delete()  # 在数据库中删除
        print('是文件')
        return JsonResponse({'status': True})




