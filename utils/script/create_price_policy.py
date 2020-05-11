import base
from web import models

"""
class PricePolicy(models.Model):
  
    
    category = models.CharField(verbose_name='策略类型', max_length=32)
    price = models.CharField(verbose_name='价格', max_length=64)
    project_length = models.PositiveSmallIntegerField(verbose_name='创建项目个数')
    team_member = models.PositiveSmallIntegerField(verbose_name='项目成员个数')
    project_capacity = models.IntegerField(verbose_name='项目空间')
    single_file_capacity = models.IntegerField(verbose_name='单文件最大容量')
    create_time = models.DateTimeField(verbose_name='创建时间')

"""
def init_price_policy():
    exists = models.PricePolicy.objects.filter(title='个人免费版', category=1).exists()
    if not exists:
        models.PricePolicy.objects.create(title='个人免费版',category=1, price=0, project_length=3, team_member=2, project_capacity=20, single_file_capacity=5)


if __name__ == '__main__':
    init_price_policy()