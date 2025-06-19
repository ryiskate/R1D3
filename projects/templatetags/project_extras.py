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
        
@register.filter(name='add_class')
def add_class(field, css_class):
    """
    Add a CSS class to a Django form field.
    Usage: {{ form.field|add_class:"form-control" }}
    """
    if hasattr(field, 'as_widget'):
        return field.as_widget(attrs={"class": css_class})
    else:
        # If it's not a form field object (e.g., it's already rendered as a string),
        # just return it unchanged
        return field

@register.filter
def replace_underscore(value):
    """
    Replaces underscores with spaces in a string
    Usage: {{ 'game_development'|replace_underscore }} -> 'game development'
    """
    if value is None:
        return ''
    return str(value).replace('_', ' ')
        
@register.filter
def percentage(value, total):
    """
    Calculates the percentage of value to total
    """
    try:
        if total == 0:
            return 0
        return int((float(value) / float(total)) * 100)
    except (ValueError, ZeroDivisionError, TypeError):
        return 0
