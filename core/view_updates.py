"""
This file contains updated code for the R1D3TaskDetailView.get_context_data method
to include subtasks in the context. Please manually apply this change to the
core/views.py file in the R1D3TaskDetailView class.
"""

# Updated get_context_data method for R1D3TaskDetailView
def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['section_name'] = getattr(self, 'section_name', 'Task')
    context['active_department'] = getattr(self, 'active_department', 'r1d3')
    
    # Get subtasks for this task
    from django.contrib.contenttypes.models import ContentType
    from projects.task_models import SubTask
    
    task = self.get_object()
    content_type = ContentType.objects.get_for_model(task.__class__)
    subtasks = SubTask.objects.filter(
        content_type=content_type,
        object_id=task.id
    ).order_by('created_at')
    
    context['subtasks'] = subtasks
    return context
