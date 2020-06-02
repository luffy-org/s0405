from django import template
from django.urls import reverse

from web.models import Project, ProjectUser

register = template.Library()


@register.inclusion_tag('inclusion/all_project.html')
def all_project(request):
    """实现下拉框显示项目功能"""
    # project_id = request.tracer.project.id
    user = request.tracer.user
    my_project = Project.objects.filter(creator=user)
    join_project = ProjectUser.objects.filter(user=user)

    return {'my_project': my_project, 'join_project': join_project, 'request': request}


@register.inclusion_tag('inclusion/manage_menu_list.html')
def manage_menu_list(request):
    """展示功能按钮与实现项目菜单默认选中"""

    url = request.path_info
    new_menu_list = [
        {'title': '概览', 'url': reverse('dashboard', kwargs={'project_id': request.tracer.project.id})},
        {'title': '统计', 'url': reverse('statistics', kwargs={'project_id': request.tracer.project.id})},
        {'title': '问题', 'url': reverse('issues', kwargs={'project_id': request.tracer.project.id})},
        {'title': '文件', 'url': reverse('file', kwargs={'project_id': request.tracer.project.id})},
        {'title': 'wiki', 'url': reverse('wiki', kwargs={'project_id': request.tracer.project.id})},
        {'title': '设置', 'url': reverse('setting', kwargs={'project_id': request.tracer.project.id})},
    ]

    for item in new_menu_list:
        if url.startswith(item['url']):
            item['is_active'] = True

    return {'new_menu_dict': new_menu_list}
