from django import template

from web.models import PorjectFile

register = template.Library()


@register.inclusion_tag('inclusion/menu_file.html')
def file_breadcrumb(data_list):
    data_list[-1]
    return {}











