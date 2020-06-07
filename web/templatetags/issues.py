from django import template

register = template.Library()


@register.simple_tag()
def issues_index(id):
    if id < 100:
        id = str(id).rjust(3, '0')
    return '#{}'.format(id)