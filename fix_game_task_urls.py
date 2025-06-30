"""
Script to check and fix the URL patterns in the game task dashboard
"""
import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'company_system.settings')
django.setup()

from django.urls import reverse, NoReverseMatch
from projects.task_models import GameDevelopmentTask

def check_url_patterns():
    """Check if the URL patterns for game tasks are correctly defined"""
    try:
        # Check if the game task delete URL pattern is correctly defined
        task_id = 24  # Example task ID
        delete_url = reverse('games:task_delete', kwargs={'pk': task_id})
        print(f"Game task delete URL pattern is correctly defined: {delete_url}")
        
        # Check if the task exists in the GameDevelopmentTask model
        task = GameDevelopmentTask.objects.filter(id=task_id).first()
        if task:
            print(f"Task ID {task_id} exists in GameDevelopmentTask model: {task.title}")
        else:
            print(f"Task ID {task_id} does not exist in GameDevelopmentTask model")
            
        return True
    except NoReverseMatch as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    print("Checking URL patterns for game tasks...")
    check_url_patterns()
    print("Done.")
