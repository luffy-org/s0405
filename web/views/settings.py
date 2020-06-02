from django.shortcuts import render, redirect

from utils.Tencent.Cos import delete_bucket
from web.models import PorjectFile, Project


def setting(request, project_id):
    return render(request, 'settings.html')


def setting_delete(request, project_id):
    print(request.POST)
    if request.method == 'GET':
        return render(request, 'setting_delete.html')
    project_title = request.POST.get('setting_delete', '')

    if not project_title or project_title != request.tracer.project.name:
        return render(request, 'setting_delete.html', {'error': '项目名错误'})

    if request.tracer.user != request.tracer.project.creator:
        return render(request, 'setting_delete.html', {'error': '只能删除自己的项目'})

    # 通过校验，进行删除
    delete_bucket(request.tracer.project.bucket)
    # 删除数据库
    Project.objects.filter(name=project_title, creator=request.tracer.user).delete()
    return redirect('list_project')
