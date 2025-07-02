"""
Context processors for the R1D3 system.
These functions add variables to the template context for all templates.
"""

def breadcrumbs_processor(request):
    """
    Add empty breadcrumbs list to context if not already present.
    Views can populate this list with breadcrumb items.
    
    Each breadcrumb item should be a dictionary with 'title' and 'url' keys.
    The last item in the list will be marked as active (no link).
    
    Example:
    breadcrumbs = [
        {'title': 'Dashboard', 'url': '/dashboard/'},
        {'title': 'Tasks', 'url': '/tasks/'},
        {'title': 'Task Title', 'url': None}  # Last item has no URL
    ]
    """
    return {
        'breadcrumbs': getattr(request, 'breadcrumbs', [])
    }
