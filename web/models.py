from django.db import models


# Create your models here.
class UserInfo(models.Model):
    """
    用户信息表
    """
    username = models.CharField(verbose_name='用户名', max_length=64)
    password = models.CharField(verbose_name='密码', max_length=32)
    mobile_phone = models.CharField(verbose_name='手机', max_length=64)
    email = models.EmailField(verbose_name='邮箱', max_length=64)

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = "01-用户信息表"
        db_table = verbose_name
        verbose_name_plural = verbose_name


class PricePolicy(models.Model):
    """
    价格策略表
    """
    title = models.CharField(verbose_name='策略名称', max_length=64, null=True)
    category_choices = ((1, '免费版'), (2, '收费版'), (3, '其他'))
    category = models.SmallIntegerField(verbose_name='策略类型', choices=category_choices, default=1)
    price = models.PositiveIntegerField(verbose_name='价格')
    project_length = models.PositiveSmallIntegerField(verbose_name='创建项目个数')
    team_member = models.PositiveSmallIntegerField(verbose_name='项目成员个数')
    project_capacity = models.IntegerField(verbose_name='项目空间', help_text='GB')
    single_file_capacity = models.IntegerField(verbose_name='单文件最大容量', help_text='MB')
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return self.category

    class Meta:
        verbose_name = "02-价格策略表"
        db_table = verbose_name
        verbose_name_plural = verbose_name


class OrderRecord(models.Model):
    """
    交易记录表
    """
    status_choice = ((0, '未支付'), (1, '已支付'))
    status = models.IntegerField(choices=status_choice, verbose_name='交易状态')
    order = models.CharField(verbose_name='订单号', max_length=64, unique=True, null=True)
    user = models.ForeignKey(to='UserInfo', verbose_name='该交易关联的用户')
    price = models.ForeignKey(to='PricePolicy', verbose_name='该交易关联的价格策略')
    count = models.SmallIntegerField(verbose_name='数量(年)', help_text='0表示无期限', default=0)
    actual_payment = models.IntegerField(verbose_name='实际支付价格', null=True, blank=True)
    start_time = models.DateTimeField(verbose_name='订单生成时间', null=True, blank=True)
    pay_time = models.DateTimeField(verbose_name='付款时间', null=True, blank=True)
    end_time = models.DateTimeField(verbose_name='结束时间', null=True, blank=True)

    class Meta:
        verbose_name = "03-交易记录表"
        db_table = verbose_name
        verbose_name_plural = verbose_name


class Project(models.Model):
    """
    项目表
    """
    color_choice = (
        (1, "#56b8eb"),  # 56b8eb
        (2, "#f28033"),  # f28033
        (3, "#ebc656"),  # ebc656
        (4, "#a2d148"),  # a2d148
        (5, "#20BFA4"),  # #20BFA4
        (6, "#7461c2"),  # 7461c2,
        (7, "#20bfa3"),  # 20bfa3,)
    )

    name = models.CharField(verbose_name='项目名称', max_length=64)
    color = models.SmallIntegerField(choices=color_choice, verbose_name='颜色', default=1)
    desc = models.CharField(verbose_name='项目描述', max_length=255, null=True, blank=True)
    use_space = models.BigIntegerField(verbose_name='项目已使用空间', default=0, help_text='字节B')
    star = models.BooleanField(verbose_name='星标项目', default=False)
    join_count = models.SmallIntegerField(verbose_name='参与项目人数', default=1)
    creator = models.ForeignKey(to='UserInfo', verbose_name='项目创建者')
    create_datetime = models.DateTimeField(auto_now_add=True, verbose_name='项目创建时间')
    bucket = models.CharField(verbose_name='cos桶', max_length=128)
    region = models.CharField(verbose_name='cos区域', max_length=32)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "04-项目表"
        db_table = verbose_name
        verbose_name_plural = verbose_name


class ProjectUser(models.Model):
    """
    项目与参与者关系表
    """
    user = models.ForeignKey(to='UserInfo', verbose_name='项目参与者')
    project = models.ForeignKey(to='Project', verbose_name='参与的项目')
    star = models.BooleanField(verbose_name='星标项目', default=False)
    create_datetime = models.DateTimeField(auto_now_add=True, verbose_name='参与项目时间')

    class Meta:
        verbose_name = "05-项目参与表"
        db_table = verbose_name
        verbose_name_plural = verbose_name


class Wiki(models.Model):
    """项目功能之wiki功能的数据库"""
    title = models.CharField(verbose_name='wiki标题', max_length=128)
    content = models.TextField(verbose_name='wiki内容')
    project = models.ForeignKey(to='Project', verbose_name='属于哪个项目')
    parent = models.ForeignKey(to='self', verbose_name='选择父wiki', null=True, blank=True)
    depth = models.IntegerField(verbose_name='深度', default=1)

    class Meta:
        verbose_name = '06-项目的wiki表'
        db_table = verbose_name
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title


class PorjectFile(models.Model):
    """项目之文件的表"""
    title = models.CharField(verbose_name='文件夹名称', max_length=128)
    project = models.ForeignKey(to='Project', verbose_name='关联的项目')
    parent = models.ForeignKey(to='self', verbose_name='属于哪个文件', null=True, blank=True)
    file_type_choice = ((1, '文件夹'), (2, '文件'))
    file_type = models.SmallIntegerField(verbose_name='文件类型', choices=file_type_choice, default=1)
    file_capacity = models.IntegerField(verbose_name='文件大小', null=True, blank=True)
    file_path = models.CharField(max_length=255, verbose_name='文件url', null=True, blank=True)
    key = models.CharField(verbose_name='COS中的名称', max_length=128, null=True, blank=True)
    update_user = models.ForeignKey(to='UserInfo', verbose_name='更新者')
    update_datetime = models.DateTimeField(auto_now=True, verbose_name='更新者')

    class Meta:
        verbose_name = '07-项目的文件表'
        db_table = verbose_name
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title


class Issues(models.Model):
    """项目问题表"""
    project = models.ForeignKey(to='Project', verbose_name='关联的项目')
    title = models.CharField(max_length=64, verbose_name='问题标题')
    desc = models.TextField(verbose_name='问题描述')
    issues_type = models.ForeignKey(to='IssuesType', verbose_name='问题属于哪个类型')
    issues_model = models.ForeignKey(to='IssuesModel', verbose_name='问题属于哪个模块', null=True, blank=True)
    status_choice = (
        (1, '处理中'),
        (2, '已解决'),
        (3, '新建'),
        (4, '已忽略'),
        (5, '待反馈'),
        (6, '已关闭'),
        (7, '重新打开'),
    )
    status = models.IntegerField(choices=status_choice, verbose_name='问题状态', default=1)
    # 使用字符串是为了在前端中可以和类名进行拼接
    level_choice = (('success', '普通'), ('warning', '紧急'), ('danger', '非常紧急'))
    level = models.CharField(choices=level_choice, max_length=12, verbose_name='问题优先级', default='danger')

    assign = models.ForeignKey(to='UserInfo', verbose_name='问题指派', null=True, blank=True, related_name='issues_assign')
    attention = models.ManyToManyField(to='UserInfo', verbose_name='问题关注者', blank=True, related_name='issues_attention')
    start_date = models.DateField(verbose_name='开始时间', null=True, blank=True)
    end_date = models.DateField(verbose_name='结束时间', null=True, blank=True)
    mode_choices = (
        (1, '公开模式'),
        (2, '隐私模式'),
    )
    mode = models.SmallIntegerField(verbose_name='模式', choices=mode_choices, default=1)
    parent = models.ForeignKey(verbose_name='父问题', to='self', related_name='child', null=True, blank=True,
                               on_delete=models.SET_NULL)
    creator = models.ForeignKey(verbose_name='创建者', to='UserInfo', related_name='create_problems')

    create_datetime = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    latest_update_datetime = models.DateTimeField(verbose_name='最后更新时间', auto_now=True)

    class Meta:
        verbose_name = '08-项目的问题表'
        db_table = verbose_name
        verbose_name_plural = verbose_name


class IssuesType(models.Model):
    """问题类型表"""
    PROJECT_INIT_LIST = ["任务", '功能', 'Bug']
    name = models.CharField(max_length=32, verbose_name='问题类型')
    project = models.ForeignKey(to='Project', verbose_name='关联的项目')

    class Meta:
        verbose_name = '09-问题表的类型表'
        db_table = verbose_name
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class IssuesModel(models.Model):
    """问题的模块(里程碑)"""
    name = models.CharField(max_length=32, verbose_name='问题模块')
    project = models.ForeignKey(to='Project', verbose_name='关联的项目')

    class Meta:
        verbose_name = '10-问题表的里程碑表'
        db_table = verbose_name
        verbose_name_plural = verbose_name


class IssuesReply(models.Model):
    """问题评论、操作记录表"""
    reply_type_choice = (
        (1, '操作记录'),
        (2, '回复'),
        (3, '评论')
    )
    reply_type = models.IntegerField(choices=reply_type_choice, verbose_name='类型')
    issues = models.ForeignKey(to='Issues', verbose_name='问题')
    content = models.TextField(verbose_name='描述')
    creator = models.ForeignKey(to='UserInfo', verbose_name='创建者')
    create_datetime = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    parent_reply = models.ForeignKey(to='self', verbose_name='父评论', null=True, blank=True)

    class Meta:
        verbose_name = '11-问题的评论表'
        db_table = verbose_name
        verbose_name_plural = verbose_name
