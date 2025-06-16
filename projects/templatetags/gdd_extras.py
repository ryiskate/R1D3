from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Template filter to get an item from a dictionary by key.
    Used in GDD detail template to access tasks for each section.
    
    Usage: {{ sections_with_tasks|get_item:section.id }}
    """
    if dictionary is None:
        return None
    
    try:
        key = int(key)  # Convert to int if it's a string representation of an int
    except (ValueError, TypeError):
        pass
    
    return dictionary.get(key)

@register.filter
def format_status(value):
    """
    Template filter to format status values by replacing underscores with spaces and capitalizing.
    Used in GDD feature formsets to display status badges.
    
    Usage: {{ feature_form.instance.status|format_status }}
    """
    if not value:
        return ""
    
    return value.replace('_', ' ').title()
