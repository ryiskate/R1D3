from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from projects.task_models import SubTask

def get_task_subtasks(task):
    """
    Get subtasks for a given task instance.
    
    Args:
        task: The task model instance
        
    Returns:
        QuerySet of SubTask objects associated with the task
    """
    content_type = ContentType.objects.get_for_model(task.__class__)
    return SubTask.objects.filter(
        content_type=content_type,
        object_id=task.id
    ).order_by('created_at')


def get_subtask_by_id(subtask_id):
    """
    Get a subtask by its ID.
    
    Args:
        subtask_id: The ID of the subtask
        
    Returns:
        SubTask object or None if not found
    """
    try:
        return SubTask.objects.get(id=subtask_id)
    except SubTask.DoesNotExist:
        return None
