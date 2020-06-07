from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from web.forms.issues import IssuseModelForm, IssuesReplyModelForm
from web.models import Issues, IssuesReply
from utils.pagination import Pagination
from django.views.decorators.csrf import csrf_exempt


def issues(request, project_id):
    if request.method == 'GET':
        queryset = Issues.objects.filter(project=request.tracer.project)
        page_object = Pagination(
            current_page=request.GET.get('page'),  # 传入当前页码
            all_count=queryset.count(),  # 传入数据总数
            base_url=request.path_info,  # 传入基础URL，既不带参数的URL
            query_params=request.GET,  # 传入url中的get条件
            per_page=2
        )
        issues_list = queryset[page_object.start: page_object.end]  # 根据分页来对总数据进行切片
        form = IssuseModelForm(request)
        context = {
            'forms': form,
            'issues': issues_list,
            'page_html': page_object.page_html()
        }
        return render(request, 'issues.html', context)

    form = IssuseModelForm(request, data=request.POST)
    if form.is_valid():
        form.instance.project = request.tracer.project
        form.instance.creator = request.tracer.user
        form.save()
        return JsonResponse({'status': True})

    return JsonResponse({'status': False, 'error': form.errors})


def issues_detail(request, project_id, issues_id):
    """具体问题的视图函数"""
    if request.method == 'GET':
        issues_obj = Issues.objects.filter(project=project_id, id=issues_id).first()
        if not issues_obj:
            return HttpResponse('详细问题错误')
        form = IssuseModelForm(request, instance=issues_obj)
        return render(request, 'issues_detail.html', {'forms': form, 'issues_obj': issues_obj})


@csrf_exempt
def issues_reply(request, project_id, issues_id):
    """获取问题的评论"""

    issues_obj = Issues.objects.filter(project=project_id, id=issues_id).first()
    if not issues_obj:
        return JsonResponse({'status': False, })
    if request.method == 'GET':
        # 查询结果，返回给前端
        ret_querysert = IssuesReply.objects.filter(issues=issues_obj, issues__project=project_id).all()  # 拿到该问题所有的评论

        # ORM查询得到的QuerySet数据类型，不能直接通过json序列化，需要先转换成字典。
        data_list = []
        for row in ret_querysert:
            data = {
                'id': row.id,
                'reply_type': row.get_reply_type_display(),
                'content': row.content,
                'creator': row.creator.username,
                'create_datetime': row.create_datetime.strftime('%Y-%m-%d %H:%M'),
                'parent_reply': row.parent_reply_id
            }
            data_list.append(data)

        return JsonResponse({'status': True, 'data': data_list})
    print(request.POST)

    form = IssuesReplyModelForm(data=request.POST)
    if form.is_valid():
        parent = form.cleaned_data.get('parent_reply')
        if parent:
            form.instance.reply_type = 2
        else:
            form.instance.reply_type = 3
        form.instance.issues_id = issues_id
        form.instance.creator = request.tracer.user
        instance = form.save()
        print('创建完成')
        info = {
            'id': instance.id,
            'creator': instance.creator.username,
            'content': instance.content,
            'reply_type': instance.get_reply_type_display(),
            'create_datetime': instance.create_datetime.strftime('%Y-%m-%d %H:%M'),
            'parent_reply': instance.parent_reply_id
        }
        return JsonResponse({'status': True, 'data': info})
    print(form.errors)

    return JsonResponse({'status': False, 'error': form.errors})
