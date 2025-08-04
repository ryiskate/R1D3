from django import template
from django.template.defaultfilters import floatformat

register = template.Library()

@register.filter
def percentage(value, total):
    """
    Calculate percentage of value relative to total.
    Returns 0 if total is 0 to avoid division by zero.
    """
    try:
        if total == 0:
            return 0
        return floatformat((value / total) * 100, 0)
    except (ValueError, TypeError):
        return 0
