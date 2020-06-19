import time

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect

from utils.Tencent.Cos import create_bucket
from web.forms.project import ProjectModelForm
from web.models import Project, ProjectUser, IssuesType


def list_project(request):
    """展示项目和添加项目功能"""
    if request.method == 'GET':
        user_obj = request.tracer.user
        user_project_dict = {"star": [], "join": [], "my": []}
        project_list = Project.objects.filter(creator=user_obj)
        for item in project_list:
            if item.star:
                user_project_dict['star'].append({'value': item, 'type': 'my'})
            else:
                user_project_dict['my'].append(item)
        join_project_list = ProjectUser.objects.filter(user=user_obj)

        for join_project in join_project_list:
            if join_project.star:
                user_project_dict["star"].append({"value": join_project.project, "type": "join"})
            else:
                user_project_dict["join"].append(join_project.project)

        form = ProjectModelForm(request)
        return render(request, 'project_list.html', {'form': form, 'user_project_dict': user_project_dict})

    form = ProjectModelForm(request, data=request.POST)
    if form.is_valid():
        # 1. 为项目创建一个cos储存桶
        bucket = '{}-{}-1300310288'.format(request.tracer.user.mobile_phone, str(int(time.time())))
        region = 'ap-guangzhou'
        create_bucket(bucket, region)  # 为每个项目创建存储桶


        # 2， 创建项目
        project_obj = form.save(commit=False)
        project_obj.creator = request.tracer.user
        project_obj.bucket = bucket
        project_obj.region = region
        project_obj.save()


        # 3. 项目初始化创建一个问题类型
        # 批量写入数据库
        issues_type_object_list = []
        for item in IssuesType.PROJECT_INIT_LIST:  # 循环默认的问题类型
            issues_type_object_list.append(IssuesType(name=item, project=project_obj))
        IssuesType.objects.bulk_create(issues_type_object_list)

        return JsonResponse({"status": True})
    return JsonResponse({"status": False, "error": form.errors})


def project_star(request, project_type, project_id):
    """添加星标项目"""
    user_obj = request.tracer.user
    if project_type == 'my':
        Project.objects.filter(id=project_id, creator=user_obj).update(star=True)
        return redirect('list_project')
    elif project_type == 'join':
        ProjectUser.objects.filter(project_id=project_id, user=user_obj).update(star=True)
        return redirect('list_project')
    return HttpResponse('加入星标错误')


def project_unstar(request, project_type, project_id):
    """取消星标"""
    user_obj = request.tracer.user
    if project_type == 'my':
        Project.objects.filter(id=project_id, creator=user_obj).update(star=False)
        return redirect('list_project')
    elif project_type == 'join':
        ProjectUser.objects.filter(project_id=project_id, user=user_obj).update(star=False)
        return redirect('list_project')
    return HttpResponse('取消星标错误')
