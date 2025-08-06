from django import template
register = template.Library()

@register.filter
def has_key(dict_obj, key):
    return key in dict_obj
