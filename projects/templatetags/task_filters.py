from django import template

register = template.Library()

@register.filter
def class_name(obj):
    """
    Returns the class name of an object.
    Usage: {{ task|class_name }}
    """
    return obj.__class__.__name__

@register.filter
def get_item(dictionary, key):
    """
    Gets an item from a dictionary by key.
    Usage: {{ dictionary|get_item:key }}
    """
    if dictionary is None:
        return None
    return dictionary.get(key)
