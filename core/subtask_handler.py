import json
from django.contrib.contenttypes.models import ContentType
from projects.task_models import SubTask

def handle_subtasks(request, task_instance):
    """
    Process subtasks from form submission and save them to the database.
    Updates existing subtasks and adds new ones from the form.
    
    Args:
        request: The HTTP request containing form data
        task_instance: The task model instance to associate subtasks with
    """
    # Get the content type for the task instance
    content_type = ContentType.objects.get_for_model(task_instance.__class__)
    
    # Get existing subtasks for this task
    existing_subtasks = SubTask.objects.filter(
        content_type=content_type,
        object_id=task_instance.id
    )
    
    # If has_subtasks is False, delete any existing subtasks and return
    if not task_instance.has_subtasks:
        existing_subtasks.delete()
        return
    
    # Get subtask data from the form
    subtask_data_list = request.POST.getlist('subtasks')
    
    # First, let's delete all existing subtasks and recreate them
    # This is the simplest way to handle title changes
    existing_subtasks.delete()
    
    # Process each subtask from the form
    for subtask_json in subtask_data_list:
        if not subtask_json:
            continue
            
        try:
            subtask_data = json.loads(subtask_json)
            title = subtask_data.get('title', '').strip()
            completed = subtask_data.get('is_completed', subtask_data.get('completed', False))
            
            # Skip empty subtasks
            if not title:
                continue
                
            # Create the subtask
            SubTask.objects.create(
                content_type=content_type,
                object_id=task_instance.id,
                title=title,
                is_completed=completed
            )
            print(f"Created/updated subtask: {title}, is_completed: {completed}")
            
        except json.JSONDecodeError:
            # Skip invalid JSON
            continue
