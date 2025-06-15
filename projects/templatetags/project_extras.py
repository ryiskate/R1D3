from django import template

register = template.Library()

@register.filter
def task_status_color(status):
    """
    Maps task status to appropriate Bootstrap color class
    """
    status_colors = {
        'backlog': 'secondary',
        'to_do': 'info',
        'in_progress': 'primary',
        'in_review': 'warning',
        'done': 'success',
        'blocked': 'danger',
    }
    return status_colors.get(status, 'secondary')

@register.filter
def get_item(dictionary, key):
    """
    Template filter to access dictionary items by key
    Usage: {{ my_dict|get_item:key_var }}
    """
    return dictionary.get(key)

@register.filter
def div(value, arg):
    """
    Divides the value by the argument
    """
    try:
        return float(value) / float(arg)
    except (ValueError, ZeroDivisionError):
        return 0
    
@register.filter
def mul(value, arg):
    """
    Multiplies the value by the argument
    """
    try:
        return float(value) * float(arg)
    except ValueError:
        return 0
    
@register.filter
def sub(value, arg):
    """
    Subtracts the argument from the value
    """
    try:
        return float(value) - float(arg)
    except ValueError:
        return 0
