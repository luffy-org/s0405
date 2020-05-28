from django import template

from web.models import PorjectFile

register = template.Library()


@register.simple_tag()
def filter_time(index):
    ret = None
    if index > 1024:
        ret = '{:.0f}KB'.format(index / 1024)
    if index > 1048576:
        ret = '{:.2f}MB'.format(index / 1048576)
    return ret
