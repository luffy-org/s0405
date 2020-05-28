import json
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from utils.Tencent.Cos import delete_object, delete_object_list, credential
from web.forms.file import FolderModelForm, FileModelForm
from web.models import PorjectFile
from django.views.decorators.csrf import csrf_exempt


def file(request, project_id):
    """文件列表、文件夹的增删改查"""
    folder_id = request.GET.get('folder_id', '')  # 获取父ID
    folder_obj = None
    if folder_id.isdecimal():  # 防止通过修改url参数
        folder_id = int(folder_id)
        folder_obj = PorjectFile.objects.filter(id=folder_id, project=request.tracer.project,
                                                file_type=1).first()  # 拿到父对象

    if request.method == 'GET':
        form = FolderModelForm(request, folder_obj)
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
            'folder_id': folder_id
        }
        return render(request, 'file.html', context)

    fid = request.POST.get('fid', '')
    file_obj = None
    if fid.isdecimal():
        file_obj = PorjectFile.objects.filter(project=request.tracer.project, id=fid).first()
    if file_obj:
        form = FolderModelForm(request, folder_obj, data=request.POST, instance=file_obj)
    else:
        form = FolderModelForm(request, folder_obj, data=request.POST)

    if form.is_valid():
        form.instance.project = request.tracer.project
        form.instance.parent = folder_obj
        form.instance.update_user = request.tracer.user
        form.save()
        print('完成创建')
        return JsonResponse({'status': True})
    print(form.errors)
    return JsonResponse({'status': False, 'errors': form.errors})


@csrf_exempt
def sts_cam(request, project_id):
    """获取临时凭证"""
    # 1. 获取到前端传递过来的文件信息列表

    result = {'status': None, 'errors': None, 'data': None}
    per_file_limit = request.tracer.price_policy.single_file_capacity * 1024 * 1024  # 单个文件大小限制 MB---> B
    total_file_limit = request.tracer.price_policy.project_capacity * 1024 * 1024 * 1024  # 项目总容量大小限制 GB --->B
    total_size = 0
    file_list = json.loads(request.body.decode('utf-8'))

    # 2. 循环判断每个文件大小是否达标

    for file_dict in file_list:
        """
        file: {'name': 'QQ31.png', 'size': 61190}
        """
        if file_dict['size'] > per_file_limit:
            result['errors'] = '{}容量超过限制，请升级套餐'.format(file_dict['name'])
            return JsonResponse(result)
        total_size += file_dict['size']

    # 3. 判断总大小是否超标
    if request.tracer.project.use_space + total_size > total_file_limit:
        result['errors'] = '总容量超过限制，请升级套餐'
        return JsonResponse(result)

    # 4. 两次判断合法后才去获取临时凭证
    response = credential(request.tracer.project.bucket, request.tracer.project.region)
    result['status'] = True
    result['data'] = response
    return JsonResponse(result)


def file_delete(request, project_id):
    """删除文件的ajax请求"""
    pid = request.GET.get('pid', '')
    ret_obj = request.tracer.project
    file_obj = PorjectFile.objects.filter(project=request.tracer.project, id=pid).first()

    if file_obj.file_type == 1:  # 如果是文件夹则需要循环删除文件夹内的所有文件
        total_size = 0
        delete_folder_list = [file_obj, ]  # 目标文件夹
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

        if delete_file_list:  # 有需要删除的文件
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
        return JsonResponse({'status': True})

@csrf_exempt
def file_add(request, project_id):
    """前端完成上传后将文件相关信息发送过来进行校验，并写入数据库"""
    result = {'status': False}
    form = FileModelForm(request, request.POST)
    if form.is_valid():
        """
        这里有一个问题，通过form.save返回的instance对象，这个对象是无法调用instance.get_xx_display()方法的
        可以利用另外一个思路去保存对象
        data_dict = form.cleaned_data
        data_dict.update({'project': request.tracer.project, 'file_type': 1, 'update_user': request.tracer.user})  # 将缺少的字段补齐
        instance = models.FileRepository.objects.create(**data_dict)
        这样得到的instance是可以调用get_xx_display()方法
        
        """
        form.instance.project = request.tracer.project
        form.instance.file_type = 2
        form.instance.update_user = request.tracer.user
        instance = form.save()
        print('完成文件添加数据库功能')
        # 完成数据库中文件的写入后对项目空间进行更新
        request.tracer.project.use_space += form.cleaned_data['file_capacity']
        request.tracer.project.save()
        # 完成数据库的写入后前端需要将数据在不刷新的情况下写到页面上，将前端需要的数据返回。
        result['status'] = True
        result_data = {
            'id': instance.id,
            'title': instance.title,
            'size': instance.file_capacity,
            'update_user': instance.update_user.username,
            'update_datetime': instance.update_datetime.strftime('%Y年%m月%d日 %H:%M')
        }
        result['data'] = result_data
        return JsonResponse(result)
    print(form.errors)
    result['errors'] = '格式错误'
    return JsonResponse(result)
