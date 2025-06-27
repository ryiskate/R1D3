from django import template

register = template.Library()

@register.filter
def class_name(obj):
    """Return the class name of an object"""
    return obj.__class__.__name__

@register.filter
def get_item(dictionary, key):
    """Get an item from a dictionary by key"""
    return dictionary.get(key, {})
