from django import template
import sys

register = template.Library()

# Debug print to confirm the filter is being loaded
print("Loading task_filters.py template filters", file=sys.stderr)

@register.filter
def class_name(obj):
    """
    Returns the class name of an object.
    Usage: {{ task|class_name }}
    """
    if obj is None:
        return ""
    class_name = obj.__class__.__name__
    print(f"class_name filter called for {obj} -> {class_name}", file=sys.stderr)
    return class_name
