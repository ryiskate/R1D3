import os
import django
import sys

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'company_system.settings')
django.setup()

# Import models after Django setup
from django.contrib.auth.models import User
from projects.game_models import GameTask, GameProject
from projects.task_models import (
    R1D3Task, GameDevelopmentTask, EducationTask,
    SocialMediaTask, ArcadeTask, ThemeParkTask
)

def list_all_tasks():
    print("\n=== TASK COUNTS ===")
    print(f"GameTask count: {GameTask.objects.count()}")
    print(f"R1D3Task count: {R1D3Task.objects.count()}")
    print(f"GameDevelopmentTask count: {GameDevelopmentTask.objects.count()}")
    print(f"EducationTask count: {EducationTask.objects.count()}")
    print(f"SocialMediaTask count: {SocialMediaTask.objects.count()}")
    print(f"ArcadeTask count: {ArcadeTask.objects.count()}")
    print(f"ThemeParkTask count: {ThemeParkTask.objects.count()}")
    
    total_tasks = (
        GameTask.objects.count() +
        R1D3Task.objects.count() +
        GameDevelopmentTask.objects.count() +
        EducationTask.objects.count() +
        SocialMediaTask.objects.count() +
        ArcadeTask.objects.count() +
        ThemeParkTask.objects.count()
    )
    print(f"Total tasks: {total_tasks}")
    
    print("\n=== GAME TASKS ===")
    for task in GameTask.objects.all():
        print(f"- {task.id}: {task.title} (Section: {task.company_section}, Status: {task.status})")
    
    print("\n=== R1D3 TASKS ===")
    for task in R1D3Task.objects.all():
        print(f"- {task.id}: {task.title} (Status: {task.status})")
    
    print("\n=== GAME DEVELOPMENT TASKS ===")
    for task in GameDevelopmentTask.objects.all():
        print(f"- {task.id}: {task.title} (Game: {task.game.title}, Status: {task.status})")
    
    print("\n=== EDUCATION TASKS ===")
    for task in EducationTask.objects.all():
        print(f"- {task.id}: {task.title} (Course: {task.course_id}, Status: {task.status})")
    
    print("\n=== SOCIAL MEDIA TASKS ===")
    for task in SocialMediaTask.objects.all():
        print(f"- {task.id}: {task.title} (Platform: {task.platform}, Status: {task.status})")
    
    print("\n=== ARCADE TASKS ===")
    for task in ArcadeTask.objects.all():
        print(f"- {task.id}: {task.title} (Machine: {task.machine_id}, Status: {task.status})")
    
    print("\n=== THEME PARK TASKS ===")
    for task in ThemeParkTask.objects.all():
        print(f"- {task.id}: {task.title} (Attraction: {task.attraction_id}, Status: {task.status})")

if __name__ == "__main__":
    list_all_tasks()
