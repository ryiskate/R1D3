import os
import django
import sys

print("Starting test task creation script...")

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'company_system.settings')
django.setup()

from django.contrib.auth.models import User
from projects.task_models import (
    R1D3Task, GameDevelopmentTask, EducationTask, 
    SocialMediaTask, ArcadeTask, ThemeParkTask
)
from datetime import date, timedelta

def create_test_tasks():
    # Find a user to assign tasks to
    try:
        user = User.objects.get(username='ricardoide')
        print(f"Found user: {user.username}")
    except User.DoesNotExist:
        user = User.objects.first()
        if user:
            print(f"Using user: {user.username}")
        else:
            print("No users found in the system. Please create a user first.")
            return
    
    # Create test tasks for each company section
    # Game Development Task
    game_task = GameDevelopmentTask.objects.create(
        title="Test Game Development Task",
        description="This is a test task for the Game Development section",
        status="to_do",
        priority="medium",
        created_by=user,
        assigned_to=user,
        due_date=date.today() + timedelta(days=7),
        platform="PC"
    )
    print(f"Created Game Development task: {game_task.id} - {game_task.title}")
    
    # Education Task
    education_task = EducationTask.objects.create(
        title="Test Education Task",
        description="This is a test task for the Education section",
        status="in_progress",
        priority="high",
        created_by=user,
        assigned_to=user,
        due_date=date.today() + timedelta(days=3),
        target_audience="Beginners"
    )
    print(f"Created Education task: {education_task.id} - {education_task.title}")
    
    # Social Media Task
    social_task = SocialMediaTask.objects.create(
        title="Test Social Media Task",
        description="This is a test task for the Social Media section",
        status="to_do",
        priority="low",
        created_by=user,
        assigned_to=user,
        due_date=date.today() + timedelta(days=1),
        platform="Twitter"
    )
    print(f"Created Social Media task: {social_task.id} - {social_task.title}")
    
    # Arcade Task
    arcade_task = ArcadeTask.objects.create(
        title="Test Arcade Task",
        description="This is a test task for the Arcade section",
        status="in_review",
        priority="medium",
        created_by=user,
        assigned_to=user,
        due_date=date.today() + timedelta(days=5),
        location="Main Arcade"
    )
    print(f"Created Arcade task: {arcade_task.id} - {arcade_task.title}")
    
    # Theme Park Task
    theme_park_task = ThemeParkTask.objects.create(
        title="Test Theme Park Task",
        description="This is a test task for the Theme Park section",
        status="done",
        priority="high",
        created_by=user,
        assigned_to=user,
        due_date=date.today() - timedelta(days=1),
        attraction="Main Attraction"
    )
    print(f"Created Theme Park task: {theme_park_task.id} - {theme_park_task.title}")
    
    print("All test tasks created successfully!")

if __name__ == "__main__":
    print("Executing main function...")
    create_test_tasks()
    print("Script execution completed.")
