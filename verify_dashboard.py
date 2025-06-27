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

def analyze_database_tasks():
    """Analyze tasks in the database"""
    # Count tasks by model
    game_tasks = list(GameTask.objects.all())
    r1d3_tasks = list(R1D3Task.objects.all())
    game_dev_tasks = list(GameDevelopmentTask.objects.all())
    education_tasks = list(EducationTask.objects.all())
    social_media_tasks = list(SocialMediaTask.objects.all())
    arcade_tasks = list(ArcadeTask.objects.all())
    theme_park_tasks = list(ThemeParkTask.objects.all())
    
    # Print counts
    print("\n=== DATABASE TASK COUNTS ===")
    print(f"GameTask count: {len(game_tasks)}")
    print(f"R1D3Task count: {len(r1d3_tasks)}")
    print(f"GameDevelopmentTask count: {len(game_dev_tasks)}")
    print(f"EducationTask count: {len(education_tasks)}")
    print(f"SocialMediaTask count: {len(social_media_tasks)}")
    print(f"ArcadeTask count: {len(arcade_tasks)}")
    print(f"ThemeParkTask count: {len(theme_park_tasks)}")
    
    total_count = len(game_tasks) + len(r1d3_tasks) + len(game_dev_tasks) + \
                 len(education_tasks) + len(social_media_tasks) + \
                 len(arcade_tasks) + len(theme_park_tasks)
    
    print(f"Total tasks: {total_count}")
    
    # Analyze GameTask company sections
    game_task_sections = {}
    for task in game_tasks:
        section = task.company_section
        if section not in game_task_sections:
            game_task_sections[section] = 0
        game_task_sections[section] += 1
    
    print("\n=== GAME TASK SECTIONS ===")
    for section, count in game_task_sections.items():
        print(f"{section}: {count} tasks")
    
    # Print task details by model
    print("\n=== TASK DETAILS ===")
    
    print("\nGameTask:")
    for task in game_tasks:
        print(f"- {task.id}: {task.title} (Section: {task.company_section}, Status: {task.status})")
    
    print("\nR1D3Task:")
    for task in r1d3_tasks:
        print(f"- {task.id}: {task.title} (Status: {task.status})")
    
    print("\nGameDevelopmentTask:")
    for task in game_dev_tasks:
        print(f"- {task.id}: {task.title} (Game: {task.game.title if task.game else 'None'}, Status: {task.status})")
    
    print("\nEducationTask:")
    for task in education_tasks:
        print(f"- {task.id}: {task.title} (Course: {task.course_id}, Status: {task.status})")
    
    print("\nSocialMediaTask:")
    for task in social_media_tasks:
        print(f"- {task.id}: {task.title} (Platform: {task.platform}, Status: {task.status})")
    
    print("\nArcadeTask:")
    for task in arcade_tasks:
        print(f"- {task.id}: {task.title} (Machine: {task.machine_id}, Status: {task.status})")
    
    print("\nThemeParkTask:")
    for task in theme_park_tasks:
        print(f"- {task.id}: {task.title} (Attraction: {task.attraction_id}, Status: {task.status})")
    
    # Return combined task list for further analysis
    return {
        'game_tasks': game_tasks,
        'r1d3_tasks': r1d3_tasks,
        'game_dev_tasks': game_dev_tasks,
        'education_tasks': education_tasks,
        'social_media_tasks': social_media_tasks,
        'arcade_tasks': arcade_tasks,
        'theme_park_tasks': theme_park_tasks,
        'total_count': total_count
    }

def simulate_dashboard_view():
    """Simulate what the dashboard view would do"""
    print("\n=== SIMULATING DASHBOARD VIEW ===")
    
    # Get all tasks from all models
    r1d3_tasks = list(R1D3Task.objects.all())
    print(f"R1D3Task count: {len(r1d3_tasks)}")
    
    game_dev_tasks = list(GameDevelopmentTask.objects.all())
    print(f"GameDevelopmentTask count: {len(game_dev_tasks)}")
    
    education_tasks = list(EducationTask.objects.all())
    print(f"EducationTask count: {len(education_tasks)}")
    
    social_media_tasks = list(SocialMediaTask.objects.all())
    print(f"SocialMediaTask count: {len(social_media_tasks)}")
    
    arcade_tasks = list(ArcadeTask.objects.all())
    print(f"ArcadeTask count: {len(arcade_tasks)}")
    
    theme_park_tasks = list(ThemeParkTask.objects.all())
    print(f"ThemeParkTask count: {len(theme_park_tasks)}")
    
    old_game_tasks = list(GameTask.objects.all())
    print(f"Old GameTask count: {len(old_game_tasks)}")
    
    # Combine all tasks into a single list
    all_tasks = r1d3_tasks + game_dev_tasks + education_tasks + social_media_tasks + arcade_tasks + theme_park_tasks + old_game_tasks
    print(f"Total combined tasks: {len(all_tasks)}")
    
    # Sort tasks by created_at (newest first)
    tasks = sorted(all_tasks, key=lambda x: x.created_at, reverse=True)
    
    # Print first 5 tasks
    print("\nFirst 5 tasks (sorted by created_at):") 
    for i, task in enumerate(tasks[:5]):
        task_type = task.__class__.__name__
        print(f"{i+1}. [{task_type}] {task.title} (Status: {task.status})")
    
    return len(tasks)

def main():
    # Analyze database tasks
    task_data = analyze_database_tasks()
    
    # Simulate dashboard view
    dashboard_task_count = simulate_dashboard_view()
    
    # Compare counts
    print("\n=== COMPARISON ===")
    print(f"Database total task count: {task_data['total_count']}")
    print(f"Dashboard simulated task count: {dashboard_task_count}")
    
    if task_data['total_count'] == dashboard_task_count:
        print("SUCCESS: Dashboard should be showing all tasks!")
        print("\nINSTRUCTIONS:")
        print("1. Log in to the dashboard at http://127.0.0.1:8000/dashboard/")
        print("2. Verify that all tasks are displayed in the table")
        print("3. Check that tasks from all models have appropriate badges")
        print("4. Test the filtering functionality for all company sections")
    else:
        print(f"WARNING: Dashboard might not be showing all tasks.")
        print("There may be an issue with the dashboard view or template.")
        print("Check the GlobalTaskDashboardView in core/views.py")
        print("and the template in templates/core/global_task_dashboard.html")

if __name__ == "__main__":
    main()
