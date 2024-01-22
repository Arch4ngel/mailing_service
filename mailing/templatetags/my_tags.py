import datetime
from django import template

register = template.Library()


# Создание тега
@register.simple_tag
def current_time(format_string):
    return datetime.datetime.now().strftime(format_string)


@register.simple_tag
@register.filter(needs_autoescape=True)
def mediapath(path):
    if path:
        return f'media/{path}'
