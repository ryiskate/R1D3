"""
Script to delete the game task with ID 24
"""
import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'company_system.settings')
django.setup()

from projects.task_models import GameDevelopmentTask
from django.contrib.auth import get_user_model

User = get_user_model()

def delete_game_task(task_id):
    """Delete a game task by ID"""
    try:
        # Find the task
        task = GameDevelopmentTask.objects.get(id=task_id)
        task_title = task.title
        
        # Delete the task
        task.delete()
        print(f"Successfully deleted game task '{task_title}' (ID: {task_id})")
        return True
    except GameDevelopmentTask.DoesNotExist:
        print(f"Game task with ID {task_id} does not exist")
        return False
    except Exception as e:
        print(f"Error deleting game task: {e}")
        return False

if __name__ == "__main__":
    task_id = 24
    print(f"Attempting to delete game task with ID {task_id}...")
    delete_game_task(task_id)
    print("Done.")
