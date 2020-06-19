import datetime

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils.safestring import mark_safe

from utils.encrypt import uid
from web.forms.issues import IssuseModelForm, IssuesReplyModelForm, ProjectInviteModelForm
from web.models import Issues, IssuesReply, ProjectUser, IssuesType, OrderRecord, ProjectInvite, PricePolicy
from utils.pagination import Pagination
from django.views.decorators.csrf import csrf_exempt
import json


class CheckFilter:
    """生成checkbox筛选按钮"""

    def __init__(self, name, data_list, request):
        self.name = name
        self.data_list = data_list
        self.request = request

    def __iter__(self):
        for item in self.data_list:
            key = str(item[0])  # request.get出来的都是字符串
            text = item[1]

            value_list = self.request.GET.getlist(self.name)

            if key in value_list:
                ck = 'checked'
                value_list.remove(key)
            else:
                ck = ''
                value_list.append(key)

            # value_list 已经完成了修改, 每个a标签添加了自己的参数
            query_dict = self.request.GET.copy()
            query_dict._mutable = True
            # 将完成修改的url放入QueryDict中，追加到之前的参数里
            query_dict.setlist(self.name, value_list)
            # urlencode方法将QueryDict数据变成合法的url
            if 'page' in query_dict:
                query_dict.pop('page')
            param_url = query_dict.urlencode()
            if param_url:
                url = '{}?{}'.format(self.request.path_info, param_url)

            else:
                url = self.request.path_info

            tpl = '<a class="cell" href="{}"><input type="checkbox" {} /><label>{}</label></a>'.format(url, ck, text)
            yield mark_safe(tpl)


"""

<select class="js-example-basic-single form-control" name="state[]" multiple>
                                <option value="AL">阿里巴巴</option>
                                
                            </select>


"""


class SelectFilter:
    """生成select筛选按钮"""

    def __init__(self, name, data_list, request):
        """
        初始化方法
        :param name:  用于在url中生成参数的key值
        :param data_list:  数据库中的条件
        :param request:    request
        """
        self.name = name
        self.data_list = data_list
        self.request = request

    def __iter__(self):
        """
        迭代方法，前端中循环该对象会触发该方法
        :return:  经过mark_safe的html内容，会在模版中渲染成按钮
        """
        yield mark_safe('<select class="js-example-basic-single form-control" name="state[]" multiple>')
        """
        [(7, 'CodeHeng'), (1, 'heng'), (8, 'fang')]
        """
        for user_info in self.data_list:
            key = str(user_info[0])
            username = user_info[1]
            # 获取当前url中是否有相同条件的参数，考虑已经筛选的情况
            value_list = self.request.GET.getlist(self.name)
            if key in value_list:  # 当前条件已经有选中的
                selected = 'selected'
                value_list.remove(key)
            else:
                selected = ''
                value_list.append(key)
            query_dict = self.request.GET.copy()
            query_dict._mutable = True
            query_dict.setlist(self.name, value_list)
            param_url = query_dict.urlencode()
            if param_url:
                url = '{}?{}'.format(self.request.path_info, param_url)
            else:
                url = self.request.path_info
            html = '<option value="{url}" {selected}>{username}</option>'.format(url=url, selected=selected,
                                                                                 username=username)
            yield mark_safe(html)

        yield mark_safe('</select>')


def issues(request, project_id):
    """问题的列表页面"""
    if request.method == 'GET':

        # 1. 获取筛选条件
        allow_filter_name = ['issues_type', 'issues_model', 'status', 'level', 'assign', 'attention', 'mode']
        condition = {}
        # 1.1 循环的去获取筛选条件
        for item in allow_filter_name:
            value_list = request.GET.getlist(item)
            if value_list:
                condition['{}__in'.format(item)] = value_list

        queryset = Issues.objects.filter(project=request.tracer.project).filter(**condition)
        page_object = Pagination(
            current_page=request.GET.get('page'),  # 传入当前页码
            all_count=queryset.count(),  # 传入数据总数
            base_url=request.path_info,  # 传入基础URL，既不带参数的URL
            query_params=request.GET,  # 传入url中的get条件
            per_page=5
        )
        issues_list = queryset[page_object.start: page_object.end]  # 根据分页来对总数据进行切片
        form = IssuseModelForm(request)
        project_issues_type = IssuesType.objects.filter(project=request.tracer.project).values_list(
            'id', 'name')
        project_total_user = [(request.tracer.project.creator.pk, request.tracer.project.creator.username)]  # 项目创建者
        project_user_queryset = ProjectUser.objects.filter(project_id=project_id).values_list('user__pk',
                                                                                              'user__username')  # 按格式输出的参与该项目的用户ID和用户名
        project_total_user.extend(project_user_queryset)
        filter_list = [
            {'title': '问题类型', 'data': CheckFilter('issues_type', project_issues_type, request)},
            {'title': '问题状态', 'data': CheckFilter('status', Issues.status_choice, request)},
            {'title': '问题优先级', 'data': CheckFilter('level', Issues.level_choice, request)},
            {'title': '问题指派', 'data': SelectFilter('assign', project_total_user, request)},
            {'title': '问题关注者', 'data': SelectFilter('attention', project_total_user, request)},
        ]

        # 邀请码模态框
        inviteform = ProjectInviteModelForm()
        context = {
            'forms': form,
            'issues': issues_list,
            'page_html': page_object.page_html(),
            'filter_list': filter_list,
            'invite_form': inviteform
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
                    print('field_name', field_name)
                    print('project_user.user', project_user.user)
                    print('issues_obj', issues_obj)
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


def issues_invite(request, project_id):
    form = ProjectInviteModelForm(data=request.POST)
    if form.is_valid():
        if request.tracer.user != request.tracer.project.creator:
            form.add_error('period', '无权创建邀请码')
            return JsonResponse({'status': False, 'error': form.errors})

        code = uid(request.tracer.user.mobile_phone)  # 生成一个随机码
        form.instance.project = request.tracer.project
        form.instance.code = code
        form.instance.creator = request.tracer.user
        form.save()

        # 将邀请码生成url返回给用户
        url = '{}://{}{}'.format(request.scheme, request.get_host(),
                                 reverse('invite_join', kwargs={'code': code}))

        return JsonResponse({'status': True, 'data': url})

    return JsonResponse({'status': False, 'error': form.errors})


def invite_join(request, code):
    # 1 判断是否是项目创建者
    current_datetime = datetime.datetime.now()
    project_invite_obj = ProjectInvite.objects.filter(code=code).first()
    if not project_invite_obj:
        return render(request, 'invite_join.html', {'error': '邀请码不合法'})
    if request.tracer.user == project_invite_obj.project.creator:
        return render(request, 'invite_join.html', {'error': '项目创建者无需加入项目'})

    # 2 判断是否已经是项目参与者
    project_user_exists = ProjectUser.objects.filter(project=project_invite_obj.project,
                                                     user=request.tracer.user).exists()
    if project_user_exists:
        return render(request, 'invite_join.html', {'error': '项目成员不用加入项目'})

    # 3 判断项目创建者的项目成员数是否已经超标
    # 3.1 拿到项目创建者的价格策略
    order_record = OrderRecord.objects.filter(user=request.tracer.user, status=1).order_by(
        '-id').first()

    if order_record.price.category == 1:  # 免费版
        # 3.1.1 如果价格策略是免费版，可以直接获取它的合法人数
        max_member = order_record.price.team_member

    else:
        # 3.1.2 如果价格策略不是免费版，则需要判断该价格策略是否过期
        if order_record.end_time < current_datetime:  # 过期
            max_member = PricePolicy.objects.filter(category=1).first().team_member
        else:
            # 没有过期
            max_member = order_record.price.team_member

    # 3.2 拿到该项目已有人数
    project_join_count = ProjectUser.objects.filter(project=project_invite_obj.project).count()
    if project_join_count >= max_member:
        return render(request, 'invite_join.html', {'error': '项目成员超过限制'})

    # 4 判断邀请码是否过期
    # 4.1 创建验证码时间 + 过期时间
    # 使用timedelta方法进行时间相加
    limit_datetime = project_invite_obj.create_datetime + datetime.timedelta(minutes=project_invite_obj.period)
    if current_datetime > limit_datetime:
        return render(request, 'invite_join.html', {'error': '邀请码过期'})

    # 5 判断邀请码是否超过设置人数
    if project_invite_obj.count:  # 如果有设置限制人数
        if project_invite_obj.user_count > project_invite_obj.count:
            return render(request, 'invite_join.html', {'error': '邀请码已超过邀请人数'})
    project_invite_obj.user_count += 1
    project_invite_obj.save()

    # 6 通过校验，将当前用户加入项目
    # 对项目参与表进行添加，这样项目参与人数也进行了增加
    ProjectUser.objects.create(user=request.tracer.user, project=project_invite_obj.project)

    # 7 对项目的参与人数数据进行更新
    project_invite_obj.project.join_count += 1
    project_invite_obj.project.save()
    return render(request, 'invite_join.html', {'project': project_invite_obj.project})
