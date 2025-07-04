from django.contrib.contenttypes.models import ContentType
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
