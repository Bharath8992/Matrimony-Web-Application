from django import template

register = template.Library()

@register.filter
def update_underscore_with_space(value):
    return value.replace("_"," ")