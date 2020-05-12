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
    project_capacity = models.IntegerField(verbose_name='项目空间')
    single_file_capacity = models.IntegerField(verbose_name='单文件最大容量')
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
    use_space = models.IntegerField(verbose_name='项目已使用空间', default=0)
    star = models.BooleanField(verbose_name='星标项目', default=False)
    join_count = models.SmallIntegerField(verbose_name='参与项目人数', default=1)
    creator = models.ForeignKey(to='UserInfo', verbose_name='项目创建者')
    create_datetime = models.DateTimeField(auto_now_add=True, verbose_name='项目创建时间')

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
    parent = models.ForeignKey(to='self', verbose_name='父wiki')

    class Meta:
        verbose_name = '06-项目的wiki表'
        db_table = verbose_name
        verbose_name_plural = verbose_name
