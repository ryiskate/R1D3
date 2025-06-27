import os
import django
import sys
from datetime import datetime, timedelta

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'company_system.settings')
django.setup()

# Import models after Django setup
from django.contrib.auth.models import User
from projects.game_models import GameProject, GameTask
from projects.task_models import (
    R1D3Task, GameDevelopmentTask, EducationTask,
    SocialMediaTask, ArcadeTask, ThemeParkTask
)

def create_test_tasks():
    # Get or create admin user
    admin_user = User.objects.filter(username='admin').first()
    if not admin_user:
        print("Creating admin user...")
        admin_user = User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    
    # Get first game project for GameDevelopmentTask
    game_project = GameProject.objects.first()
    if not game_project:
        print("No game projects found. Cannot create GameDevelopmentTask.")
        return
    
    print(f"Using game project: {game_project.title} (ID: {game_project.id})")
    
    # Common task fields
    common_fields = {
        'description': 'This is a test task created by script',
        'status': 'to_do',
        'priority': 'medium',
        'created_by': admin_user,
        'assigned_to': admin_user,
        'due_date': datetime.now().date() + timedelta(days=7),
        'estimated_hours': 5.0,
        'actual_hours': 0.0,
        'tags': 'test,script',
        'task_type': 'test'
    }
    
    # Create R1D3Task
    r1d3_task = R1D3Task.objects.create(
        **common_fields,
        title='Test R1D3 Task',
        department='General',
        impact_level='Medium',
        strategic_goal='Testing the dashboard'
    )
    print(f"Created R1D3Task: {r1d3_task.title} (ID: {r1d3_task.id})")
    
    # Create GameDevelopmentTask
    game_dev_task = GameDevelopmentTask.objects.create(
        **common_fields,
        title='Test Game Development Task',
        game=game_project,
        feature_id='TEST-001',
        platform='PC',
        build_version='0.1.0'
    )
    print(f"Created GameDevelopmentTask: {game_dev_task.title} (ID: {game_dev_task.id})")
    
    # Create EducationTask
    education_task = EducationTask.objects.create(
        **common_fields,
        title='Test Education Task',
        course_id='EDU-101',
        learning_objective='Learn about task models',
        target_audience='Developers',
        educational_level='Intermediate'
    )
    print(f"Created EducationTask: {education_task.title} (ID: {education_task.id})")
    
    # Create SocialMediaTask
    social_media_task = SocialMediaTask.objects.create(
        **common_fields,
        title='Test Social Media Task',
        platform='Twitter',
        campaign_id='SM-001',
        channel='@R1D3Games',
        target_metrics='Engagement rate > 5%',
        content_type='Announcement'
    )
    print(f"Created SocialMediaTask: {social_media_task.title} (ID: {social_media_task.id})")
    
    # Create ArcadeTask
    arcade_task = ArcadeTask.objects.create(
        **common_fields,
        title='Test Arcade Task',
        machine_id='ARC-001',
        location='Main Hall',
        maintenance_type='Routine',
        machine_model='R1D3 Deluxe'
    )
    print(f"Created ArcadeTask: {arcade_task.title} (ID: {arcade_task.id})")
    
    # Create ThemeParkTask - remove task_type from common_fields to avoid conflict
    theme_park_fields = common_fields.copy()
    theme_park_fields.pop('task_type', None)  # Remove task_type to avoid conflict
    
    theme_park_task = ThemeParkTask.objects.create(
        **theme_park_fields,
        title='Test Theme Park Task',
        attraction_id='ATT-001',
        zone='Adventure Zone',
        task_type='Maintenance',
        safety_priority='High'
    )
    print(f"Created ThemeParkTask: {theme_park_task.title} (ID: {theme_park_task.id})")
    
    print("\nAll test tasks created successfully!")

if __name__ == "__main__":
    create_test_tasks()
