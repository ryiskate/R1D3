"""
Script to identify and delete test tasks that can't be deleted through the UI
"""
import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'company_system.settings')
django.setup()

# Import task models
from projects.task_models import R1D3Task, GameDevelopmentTask, SocialMediaTask, EducationTask, ArcadeTask, ThemeParkTask
from django.db.models import Model

def check_task_existence(task_id):
    """Check if a task exists in various models and print the results"""
    print(f"\nChecking task ID {task_id}:")
    
    # Check in all specialized task models
    models_to_check = [
        (R1D3Task, "R1D3Task"),
        (GameDevelopmentTask, "GameDevelopmentTask"),
        (SocialMediaTask, "SocialMediaTask"),
        (EducationTask, "EducationTask"),
        (ArcadeTask, "ArcadeTask"),
        (ThemeParkTask, "ThemeParkTask")
    ]
    
    for model, model_name in models_to_check:
        task = model.objects.filter(id=task_id).first()
        if task:
            print(f"Found in {model_name}: {task.title}")
            return (model_name, task)
    
    print(f"Task ID {task_id} not found in any task model")
    return (None, None)

def delete_task(task_id):
    """Delete a task by ID after identifying which model it belongs to"""
    model_name, task = check_task_existence(task_id)
    
    if task:
        task_title = task.title
        try:
            task.delete()
            print(f"Successfully deleted {model_name} '{task_title}' (ID: {task_id})")
            return True
        except Exception as e:
            print(f"Error deleting task: {e}")
            return False
    else:
        print(f"Cannot delete task ID {task_id} - not found")
        return False

if __name__ == "__main__":
    # Task IDs to delete
    task_ids = [92, 98]
    
    print("Starting task deletion process...")
    
    for task_id in task_ids:
        delete_task(task_id)
    
    print("\nTask deletion process completed.")
