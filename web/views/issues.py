from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from web.forms.issues import IssuseModelForm, IssuesReplyModelForm
from web.models import Issues, IssuesReply, ProjectUser
from utils.pagination import Pagination
from django.views.decorators.csrf import csrf_exempt
import json


def issues(request, project_id):
    """问题的列表页面"""
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
    """具体问题的详细信息"""
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
        ret_querysert = IssuesReply.objects.filter(issues=issues_obj, issues__project=project_id)  # 拿到该问题所有的评论

        current_page = 1
        ajax_current_page = request.GET.get('page')
        if ajax_current_page:
            current_page = ajax_current_page

        # 分页
        page_object = Pagination(
            current_page=current_page,
            all_count=ret_querysert.count(),
            base_url=request.path_info,
            query_params=request.GET,
            per_page=10
        )

        # 根据分页需求拿到数据
        issues_record_list = ret_querysert[page_object.start: page_object.end]

        # ORM查询得到的QuerySet数据类型，不能直接通过json序列化，需要先转换成字典。
        data_list = []

        for row in ret_querysert:
            # son_relpy = row.issuesreply_set.all()

            data = {
                'id': row.id,
                'reply_type': row.get_reply_type_display(),
                'content': row.content,
                'creator': row.creator.username,
                'create_datetime': row.create_datetime.strftime('%Y-%m-%d %H:%M'),
                'parent_reply': row.parent_reply_id,
            }
            data_list.append(data)

            """
            if son_relpy:
                data = {
                    'id': row.id,
                    'reply_type': row.get_reply_type_display(),
                    'content': row.content,
                    'creator': row.creator.username,
                    'create_datetime': row.create_datetime.strftime('%Y-%m-%d %H:%M'),
                    'son_reply': serializers.serialize("json", son_relpy)

                }
                data_list.append(data)

            else:

                data = {
                    'id': row.id,
                    'reply_type': row.get_reply_type_display(),
                    'content': row.content,
                    'creator': row.creator.username,
                    'create_datetime': row.create_datetime.strftime('%Y-%m-%d %H:%M'),
                }
                data_list.append(data)
            
            """
        # test_list = ret_querysert[page_object.start: page_object.end].values('id', 'reply_type', 'content', 'creator', 'parent_reply')

        # print('data', data_list)
        context = {
            'status': True,
            'data': data_list,
            # 'page_html': page_object.page_ajax_html()
        }

        return JsonResponse(context)
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


@csrf_exempt
def issues_update(request, project_id, issues_id):
    """编辑问题"""
    res = {'status': False}
    issues_obj = Issues.objects.filter(project=project_id, id=issues_id).first()

    # 为修改数据库并创建一条修改记录写一个函数
    def create_record(text):
        instance = IssuesReply.objects.create(
            reply_type=1,
            issues_id=issues_id,
            content=text,
            creator=request.tracer.user
        )
        info = {
            'id': instance.id,
            'creator': instance.creator.username,
            'content': instance.content,
            'reply_type': instance.get_reply_type_display(),
            'create_datetime': instance.create_datetime.strftime('%Y-%m-%d %H:%M'),
            'parent_reply': instance.parent_reply_id
        }
        return info

    # 1. 获取前端传递过来的数据，因为是json所以需要先解码后在反序列化

    post_dict = json.loads(request.body.decode('utf-8'))
    print('----', post_dict)

    """
    {'name': 'title', 'value': '什么时候去九点asdfe'}
    {'name': '表中字段名', 'value': '修改该字段的值'}
    
    """
    # 2. 根据前端传递的信息，生成字段对象
    field_name = post_dict.get('name')
    field_value = post_dict.get('value')
    field_obj = Issues._meta.get_field(field_name)

    # 3. 对字段的值是字符串的进行处理
    if field_name in ['title', 'desc', 'start_date', 'end_date']:
        # 3.1 判断value值是否能为空
        if not field_value:  # 用户输入的值为空
            # 3.1.1 数据库不能为空返回错误
            if not field_obj.null:  # 数据库中不能为空
                res['error'] = '该选项不能为空'
            # 3.1.2 数据库可以为空，写入数据库，并创建一条操作记录
            else:
                setattr(issues_obj, field_name, None)
                issues_obj.save()
                content = '{}选项更新为空'.format(field_obj.verbose_name)
                res['status'] = True
                info = create_record(content)
                res['data'] = info
        # 3.2 value的值不为空
        else:
            setattr(issues_obj, field_name, field_value)
            issues_obj.save()
            if field_name == 'desc':
                content = '{} 选项进行了更新'.format(field_obj.verbose_name)
            else:
                content = '{} 选项更新为"{}"'.format(field_obj.verbose_name, field_value)
            res['status'] = True
            info = create_record(content)
            res['data'] = info

    # 4. 对一对多字段进行校验与更新
    if field_name in ['issues_type', 'issues_model', 'assign', 'parent']:
        # 此时field_value=1, 2, 3, 4 数字
        # 4.1 先判断一对多字段能否为空
        if not field_value:
            if not field_obj.null:
                res['error'] = '该选项不能为空'
            else:

                setattr(issues_obj, field_name, None)
                issues_obj.save()
                content = '{} 选项更新为空'.format(field_obj.verbose_name)
                res['status'] = True
                info = create_record(content)
                res['data'] = info
        else:
            if field_name == 'assign':  # 问题指派需要单独处理，因为它不能直接去用户表里校验，它需要通过项目参与表去校验

                project_user = ProjectUser.objects.filter(user__id=field_value, project_id=project_id).first()
                if not project_user:
                    res['error'] = '该选项不存在'
                else:
                    setattr(issues_obj, field_name, project_user.user)
                    issues_obj.save()
                    content = '{} 选项更新为{}'.format(field_obj.verbose_name, str(project_user.user))
                    res['status'] = True
                    info = create_record(content)
                    res['data'] = info

            else:
                foreignkey_obj = field_obj.rel.model.objects.filter(id=field_value, project_id=project_id).first()
                print('foreignkey_obj', foreignkey_obj)
                if not foreignkey_obj:
                    res['error'] = '该选项不存在'
                setattr(issues_obj, field_name, foreignkey_obj)  # 将一对多字段保存关联对象
                issues_obj.save()
                content = '{} 选项更新为{}'.format(field_obj.verbose_name, str(foreignkey_obj))
                res['status'] = True
                info = create_record(content)
                res['data'] = info

    # 5. choices字段
    if field_name in ['status', 'level', 'mode']:
        ret = None
        for key, item in field_obj.choices:
            if field_value in str(key):  # 说明选项合法
                ret = item
        if not ret:
            res['error'] = '该选项不存在'
        else:
            setattr(issues_obj, field_name, field_value)
            issues_obj.save()
            content = '{} 选项更新为{}'.format(field_obj.verbose_name, ret)
            res['status'] = True
            info = create_record(content)
            res['data'] = info

    # 6. 多对多字段
    if field_name == 'attention':
        # 获取用户选择，列表

        if not field_value:
            if not field_obj.null:
                res['error'] = '该选项不能为空'
            else:
                setattr(issues_obj, field_name, None)
                issues_obj.save()
                content = '{} 选项更新为空'.format(field_obj.verbose_name)
                res['status'] = True
                info = create_record(content)
                res['data'] = info

        else:

        # 1 拿到该项目的所有参与者
        # 2。 将数据设计成字段， ID， username
        # 3。 循环用户选择，判断用户选择是否在字段里
            project_user_dict = {}
            project_user_list = ProjectUser.objects.filter(project_id=project_id)
            for item in project_user_list:
                project_user_dict[item.user.id] = item.user.username
            set_user_list = []
            for val in field_value:

                if int(val) not in project_user_dict:
                    res['error'] = '该选项不存在'
                else:
                    set_user_list.append(project_user_dict[int(val)])
                    issues_obj.attention.set(field_value)
                    content = '{} 选项更新为{}'.format(field_obj.verbose_name, ','.join(set_user_list))
                    res['status'] = True
                    info = create_record(content)
                    res['data'] = info

    return JsonResponse(res)
