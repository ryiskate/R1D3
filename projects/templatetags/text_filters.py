from django import template

register = template.Library()

@register.filter
def replace_underscore(value):
    """
    Replaces underscores with spaces in a string
    Usage: {{ 'game_development'|replace_underscore }} -> 'game development'
    """
    if value is None:
        return ''
    return str(value).replace('_', ' ')
