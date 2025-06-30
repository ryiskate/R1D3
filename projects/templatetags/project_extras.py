from django import template
from datetime import date

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
        
@register.filter
def status_color(status):
    """
    Maps task status to appropriate Bootstrap color class
    """
    status_colors = {
        'backlog': 'secondary',
        'to_do': 'primary',
        'in_progress': 'warning',
        'in_review': 'info',
        'done': 'success',
        'blocked': 'danger',
    }
    return status_colors.get(status, 'secondary')

@register.filter
def status_icon(status):
    """
    Maps task status to appropriate FontAwesome icon
    """
    status_icons = {
        'backlog': 'inbox',
        'to_do': 'clipboard-list',
        'in_progress': 'spinner',
        'in_review': 'search',
        'done': 'check-circle',
        'blocked': 'ban',
    }
    return status_icons.get(status, 'question-circle')

@register.filter
def priority_color(priority):
    """
    Maps task priority to appropriate Bootstrap color class
    """
    priority_colors = {
        'low': 'success',
        'medium': 'warning',
        'high': 'danger',
        'critical': 'dark',
    }
    return priority_colors.get(priority, 'secondary')

@register.filter
def priority_icon(priority):
    """
    Maps task priority to appropriate FontAwesome icon
    """
    priority_icons = {
        'low': 'arrow-down',
        'medium': 'minus',
        'high': 'arrow-up',
        'critical': 'exclamation-triangle',
    }
    return priority_icons.get(priority, 'question-circle')

@register.filter
def is_past_due(due_date):
    """
    Checks if a due date is in the past
    """
    if not due_date:
        return False
    return due_date < date.today()
