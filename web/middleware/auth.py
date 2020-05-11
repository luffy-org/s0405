import datetime

from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin

from s0405 import settings
from web.models import UserInfo, OrderRecord, Project, ProjectUser


class Tracer:
    """
    将用户的权限信息封装到对象中
    """

    def __init__(self):
        self.user = None
        self.price_policy = None
        self.project = None


class AuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.tracer = Tracer()  # 实例化
        # 1 去session拿user_id,依据这个判断是否有登陆
        user_id = request.session.get('user_id', 0)
        # 2 根据user_id拿到用户对象
        user_obj = UserInfo.objects.filter(pk=user_id).first()
        # 3 将用户对象添加的tracer对象的user属性中
        request.tracer.user = user_obj
        if request.path_info in settings.WHITE_REGEX_URL_LIST:
            return  # 直接return程序会继续往下执行
        if not request.tracer.user:
            # 如果没有登陆，重定向到登陆页面
            return redirect('/login/')
        # 4 拿到登陆用户完成的交易(还需要考虑到一个用户可能有多次交易记录)
        # 拿到用户交易的方法一：
        # 根据交易记录表拿到所有该用户的交易，并进行排序，最新的交易记录是他的有效权限
        user_order_record = OrderRecord.objects.filter(status=1, user=request.tracer.user).order_by('-id').first()
        '''
        拿到用户的交易记录方法二：
        在用户表里添加一个价格策略字段，一个用户只能有一个有效的价格策略，所以在用户表里用ForeignKey和策略表进行关联
        根据用户的策略字段就能查询到策略表，从策略表就能对权限进行判断，省去了排序的操作
        '''
        # 5 拿到交易判断是否过期，未过期的话根据交易查询到该交易拥有的价格策略(添加项目的权限)
        date_now = datetime.datetime.now()
        if user_order_record.end_time and date_now > user_order_record.end_time:  # 代表购买的交易记录已经过期
            user_order_record = OrderRecord.objects.filter(user=request.tracer.user, status=1,
                                                           price__category=1).first()
            # 交易过期，用户的价格策略设置为免费的
        request.tracer.price_policy = user_order_record.price

    def process_view(self, request, view, args, kwargs):
        # 1. 判断是否以manage开头
        if not request.path_info.startswith('/manage/'):  # 如果不是以manage开头就不进行设置，直接return
            return
        # 2. 判断URL中的project_id是否属于当前用户的项目ID中
        project_id = kwargs.get('project_id')
        my_project = Project.objects.filter(creator=request.tracer.user, id=project_id).first()
        if my_project:
            request.tracer.project = my_project
            return
        join_project = ProjectUser.objects.filter(user=request.tracer.user, project_id=project_id).first()
        if join_project:
            request.tracer.project = join_project.project
            return
        return redirect('list_project')


