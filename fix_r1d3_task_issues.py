"""
This script fixes the R1D3 task detail display and subtask saving issues.
Run this script to apply the necessary changes to your codebase.
"""
import os
import re
import json
from pathlib import Path

def create_subtask_handler():
    """Create the subtask handler file"""
    subtask_handler_path = Path('core/subtask_handler.py')
    
    if not subtask_handler_path.exists():
        print(f"Creating {subtask_handler_path}...")
        subtask_handler_content = """import json
from django.contrib.contenttypes.models import ContentType
from projects.task_models import SubTask

def handle_subtasks(request, task_instance):
    \"\"\"
    Process subtasks from form submission and save them to the database.
    
    Args:
        request: The HTTP request containing form data
        task_instance: The task model instance to associate subtasks with
    \"\"\"
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
    
    # Track which subtasks to keep
    processed_subtasks = []
    
    # Process each subtask
    for subtask_json in subtask_data_list:
        if not subtask_json:
            continue
            
        try:
            subtask_data = json.loads(subtask_json)
            title = subtask_data.get('title', '').strip()
            completed = subtask_data.get('completed', False)
            
            # Skip empty subtasks
            if not title:
                continue
                
            # Create or update the subtask
            subtask, created = SubTask.objects.update_or_create(
                content_type=content_type,
                object_id=task_instance.id,
                title=title,
                defaults={'is_completed': completed}
            )
            
            processed_subtasks.append(subtask.id)
            
        except json.JSONDecodeError:
            # Skip invalid JSON
            continue
    
    # Delete any subtasks that weren't in the form submission
    existing_subtasks.exclude(id__in=processed_subtasks).delete()
"""
        with open(subtask_handler_path, 'w') as f:
            f.write(subtask_handler_content)
        print(f"Created {subtask_handler_path}")
    else:
        print(f"{subtask_handler_path} already exists")

def create_task_utils():
    """Create the task utils file"""
    task_utils_path = Path('core/task_utils.py')
    
    if not task_utils_path.exists():
        print(f"Creating {task_utils_path}...")
        task_utils_content = """from django.contrib.contenttypes.models import ContentType
from projects.task_models import SubTask

def get_task_subtasks(task):
    \"\"\"
    Get subtasks for a given task instance.
    
    Args:
        task: The task model instance
        
    Returns:
        QuerySet of SubTask objects associated with the task
    \"\"\"
    content_type = ContentType.objects.get_for_model(task.__class__)
    return SubTask.objects.filter(
        content_type=content_type,
        object_id=task.id
    ).order_by('created_at')
"""
        with open(task_utils_path, 'w') as f:
            f.write(task_utils_content)
        print(f"Created {task_utils_path}")
    else:
        print(f"{task_utils_path} already exists")

def update_task_update_view():
    """Update the R1D3TaskUpdateView to handle subtasks"""
    views_path = Path('core/views.py')
    
    if not views_path.exists():
        print(f"Error: {views_path} does not exist")
        return
    
    print(f"Updating {views_path} to handle subtasks in R1D3TaskUpdateView...")
    
    with open(views_path, 'r') as f:
        content = f.read()
    
    # Find the form_valid method in R1D3TaskUpdateView
    pattern = r'(def form_valid\(self, form\):\s+)(messages\.success.*?\n\s+return super\(\)\.form_valid\(form\))'
    replacement = r'\1response = super().form_valid(form)\n        \n        # Import and use the subtask handler\n        from core.subtask_handler import handle_subtasks\n        handle_subtasks(self.request, form.instance)\n        \n        messages.success(self.request, f"Task \'{form.instance.title}\' updated successfully!")\n        return response'
    
    updated_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    if updated_content != content:
        with open(views_path, 'w') as f:
            f.write(updated_content)
        print(f"Updated {views_path} to handle subtasks in R1D3TaskUpdateView")
    else:
        print(f"Could not find the form_valid method in R1D3TaskUpdateView")

def update_task_detail_view():
    """Update the R1D3TaskDetailView to include subtasks in the context"""
    views_path = Path('core/views.py')
    
    if not views_path.exists():
        print(f"Error: {views_path} does not exist")
        return
    
    print(f"Updating {views_path} to include subtasks in R1D3TaskDetailView...")
    
    with open(views_path, 'r') as f:
        content = f.read()
    
    # Find the get_context_data method in R1D3TaskDetailView
    pattern = r'(def get_context_data\(self, \*\*kwargs\):\s+context = super\(\)\.get_context_data\(\*\*kwargs\)\s+context\[\'section_name\'\] = getattr\(self, \'section_name\', \'Task\'\)\s+context\[\'active_department\'\] = getattr\(self, \'active_department\', \'r1d3\'\)\s+)(return context)'
    replacement = r'\1# Get subtasks for this task\n        from core.task_utils import get_task_subtasks\n        context[\'subtasks\'] = get_task_subtasks(self.object)\n        \n        \2'
    
    updated_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    if updated_content != content:
        with open(views_path, 'w') as f:
            f.write(updated_content)
        print(f"Updated {views_path} to include subtasks in R1D3TaskDetailView")
    else:
        print(f"Could not find the get_context_data method in R1D3TaskDetailView")

def update_task_detail_template():
    """Update the task detail template to display subtasks and fix modal forms"""
    template_path = Path('templates/projects/r1d3_task_detail.html')
    
    if not template_path.exists():
        print(f"Error: {template_path} does not exist")
        return
    
    print(f"Updating {template_path} to display subtasks and fix modal forms...")
    
    with open(template_path, 'r') as f:
        content = f.read()
    
    # Add subtasks section if it doesn't exist
    if '{% if task.has_subtasks and subtasks %}' not in content:
        subtasks_section = """
                    {% if task.has_subtasks and subtasks %}
                    <div class="row mt-3">
                        <div class="col-12">
                            <h6 class="fw-bold">Subtasks</h6>
                            <div class="mb-3">
                                <div class="card">
                                    <div class="card-body">
                                        <ul class="list-group list-group-flush">
                                            {% for subtask in subtasks %}
                                            <li class="list-group-item d-flex justify-content-between align-items-center">
                                                <div>
                                                    {% if subtask.is_completed %}
                                                    <i class="bi bi-check-circle-fill text-success me-2"></i>
                                                    <span class="text-decoration-line-through">{{ subtask.title }}</span>
                                                    {% else %}
                                                    <i class="bi bi-circle text-secondary me-2"></i>
                                                    <span>{{ subtask.title }}</span>
                                                    {% endif %}
                                                </div>
                                                <small class="text-muted">{{ subtask.updated_at|date:"M d, Y" }}</small>
                                            </li>
                                            {% endfor %}
                                        </ul>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    {% endif %}"""
        
        # Insert after the output section
        output_pattern = r'({% if task\.output %}.*?{% endif %})'
        updated_content = re.sub(output_pattern, r'\1' + subtasks_section, content, flags=re.DOTALL)
        
        if updated_content != content:
            content = updated_content
            print("Added subtasks section to template")
    
    # Fix status update modal form
    status_form_pattern = r'(<form method="post" action="#">\s+{% csrf_token %}\s+<div class="modal-body">\s+<div class="mb-3">\s+<label for="status".*?</select>\s+</div>\s+<input type="hidden" name="task_id" value="{{ task.id }}">\s+</div>)'
    status_form_replacement = r'<form method="post" action="{% url \'projects:r1d3_task_status_update\' %}">\n                {% csrf_token %}\n                <div class="modal-body">\n                    <div class="mb-3">\n                        <label for="status" class="form-label">Status</label>\n                        <select class="form-select" id="status" name="status">\n                            <option value="backlog" {% if task.status == \'backlog\' %}selected{% endif %}>Backlog</option>\n                            <option value="to_do" {% if task.status == \'to_do\' %}selected{% endif %}>To Do</option>\n                            <option value="in_progress" {% if task.status == \'in_progress\' %}selected{% endif %}>In Progress</option>\n                            <option value="in_review" {% if task.status == \'in_review\' %}selected{% endif %}>In Review</option>\n                            <option value="done" {% if task.status == \'done\' %}selected{% endif %}>Done</option>\n                            <option value="blocked" {% if task.status == \'blocked\' %}selected{% endif %}>Blocked</option>\n                        </select>\n                    </div>\n                    <input type="hidden" name="task_id" value="{{ task.id }}">\n                </div>'
    
    updated_content = re.sub(status_form_pattern, status_form_replacement, content, flags=re.DOTALL)
    
    if updated_content != content:
        content = updated_content
        print("Fixed status update modal form")
    
    # Fix hours update modal form
    hours_form_pattern = r'(<form method="post" action="#">\s+{% csrf_token %}\s+<div class="modal-body">\s+<div class="mb-3">\s+<label for="hours_spent".*?</div>\s+</div>)'
    hours_form_replacement = r'<form method="post" action="{% url \'projects:r1d3_task_hours_update\' %}">\n                {% csrf_token %}\n                <div class="modal-body">\n                    <div class="mb-3">\n                        <label for="hours_spent" class="form-label">Hours Spent</label>\n                        <input type="number" class="form-control" id="hours_spent" name="hours_spent" step="0.5" min="0" value="0">\n                    </div>\n                    <input type="hidden" name="task_id" value="{{ task.id }}">\n                </div>'
    
    updated_content = re.sub(hours_form_pattern, hours_form_replacement, content, flags=re.DOTALL)
    
    if updated_content != content:
        content = updated_content
        print("Fixed hours update modal form")
    
    # Write the updated content back to the file
    with open(template_path, 'w') as f:
        f.write(content)
    
    print(f"Updated {template_path}")

def main():
    """Main function to fix all issues"""
    print("Starting to fix R1D3 task detail display and subtask saving issues...")
    
    # Create necessary files
    create_subtask_handler()
    create_task_utils()
    
    # Update views
    update_task_update_view()
    update_task_detail_view()
    
    # Update template
    update_task_detail_template()
    
    print("\nFinished fixing R1D3 task detail display and subtask saving issues.")
    print("Please restart your Django server to apply the changes.")

if __name__ == "__main__":
    main()
