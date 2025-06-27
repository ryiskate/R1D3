"""
Script to create a test task for the R1D3 dashboard
"""
from django.contrib.auth.models import User

# Import the task models
try:
    from projects.task_models import R1D3Task
    
    # Get the first user
    user = User.objects.first()
    print(f"Found user: {user}")
    
    # Create a test task
    task = R1D3Task.objects.create(
        title='Test R1D3 Task',
        description='This is a test task for the R1D3 dashboard',
        status='to_do',
        priority='medium',
        created_by=user,
        assigned_to=user
    )
    
    print(f"Created task: {task.id} - {task.title}")
    
except Exception as e:
    print(f"Error creating task: {e}")
