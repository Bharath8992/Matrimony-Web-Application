from django import template

register = template.Library()

@register.filter
def get_attr(obj, attr):
    """Get attribute from object dynamically"""
    try:
        return getattr(obj, attr)
    except (AttributeError, TypeError):
        return None

@register.filter
def get_url(obj):
    """Get URL from ImageField or return None"""
    try:
        if obj and hasattr(obj, 'url'):
            return obj.url
    except (AttributeError, ValueError):
        pass
    return None

@register.filter
def has_attr(obj, attr):
    """Check if object has attribute and it's not empty"""
    try:
        value = getattr(obj, attr)
        return bool(value)
    except (AttributeError, TypeError):
        return False