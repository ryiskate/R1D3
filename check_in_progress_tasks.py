"""
Check for tasks with 'in_progress' status in the database.
"""
import os
import django
import sys

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'company_system.settings')
django.setup()

# Import models after Django setup
from projects.game_models import GameTask, GameMilestone
from strategy.models import StrategyPhase, StrategyMilestone

def check_in_progress_tasks():
    """Check for tasks with 'in_progress' status in the database."""
    print("\n=== CHECKING IN-PROGRESS TASKS ===\n")
    
    # Check GameTask model
    in_progress_tasks = GameTask.objects.filter(status='in_progress')
    print(f"Found {in_progress_tasks.count()} tasks with 'in_progress' status:")
    
    for task in in_progress_tasks:
        print(f"\nTask ID: {task.id}")
        print(f"Task Title: {task.title}")
        print(f"Task Status: {task.status}")
        
        if task.milestone:
            print(f"Milestone: {task.milestone.title}")
            if task.game:
                print(f"Game: {task.game.title}")
        else:
            print("No milestone associated with this task")
    
    # Check if any milestone has "Open First Arcade Location" in the title
    arcade_milestones = GameMilestone.objects.filter(title__icontains="Open First Arcade Location")
    print(f"\nFound {arcade_milestones.count()} milestones with 'Open First Arcade Location' in the title:")
    
    for milestone in arcade_milestones:
        print(f"\nMilestone ID: {milestone.id}")
        print(f"Milestone Title: {milestone.title}")
        print(f"Is Completed: {milestone.is_completed}")
        
        # Check if any tasks are associated with this milestone
        tasks = GameTask.objects.filter(milestone=milestone)
        print(f"Associated Tasks: {tasks.count()}")
        for task in tasks:
            print(f"  - {task.title} (Status: {task.status})")
    
    # Check strategy phases
    phases = StrategyPhase.objects.all()
    print(f"\nFound {phases.count()} strategy phases:")
    
    for phase in phases:
        print(f"\nPhase ID: {phase.id}")
        print(f"Phase Name: {phase.name}")
        print(f"Phase Type: {phase.phase_type}")
        print(f"Is Current: {phase.is_current}")
        print(f"Is Completed: {phase.is_completed}")

if __name__ == "__main__":
    check_in_progress_tasks()
