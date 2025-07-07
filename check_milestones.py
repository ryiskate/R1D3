"""
Script to check all milestones and their status in the database.
"""
import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'company_system.settings')
django.setup()

# Import models
from projects.game_models import GameMilestone, GameTask
from django.utils import timezone

def check_all_milestones():
    """Check all milestones in the database and their status."""
    print("\n=== ALL MILESTONES STATUS ===")
    
    # Get all milestones
    all_milestones = GameMilestone.objects.all().order_by('game__title', 'due_date')
    
    if not all_milestones:
        print("No milestones found in the database!")
        return
    
    print(f"Found {all_milestones.count()} milestones in total:")
    
    # Group milestones by status
    not_started = []
    in_progress = []
    completed = []
    
    for m in all_milestones:
        if m.status == 'not_started':
            not_started.append(m)
        elif m.status == 'in_progress':
            in_progress.append(m)
        elif m.status == 'completed':
            completed.append(m)
    
    # Print in-progress milestones (most important)
    print(f"\n=== IN PROGRESS MILESTONES ({len(in_progress)}) ===")
    for i, m in enumerate(in_progress, 1):
        print(f"{i}. {m.title} (Game: {m.game.title})")
        print(f"   Due date: {m.due_date}")
        print(f"   Status: {m.status}")
        print(f"   Description: {m.description[:50]}..." if m.description and len(m.description) > 50 else f"   Description: {m.description}")
        
        # Check for related tasks
        tasks = GameTask.objects.filter(milestone=m)
        if tasks.exists():
            print(f"   Related tasks ({tasks.count()}):")
            for j, task in enumerate(tasks[:3], 1):
                print(f"     {j}. {task.title} - Status: {task.status}")
            if tasks.count() > 3:
                print(f"     ... and {tasks.count() - 3} more tasks")
        print()
    
    # Print not started milestones
    print(f"\n=== NOT STARTED MILESTONES ({len(not_started)}) ===")
    for i, m in enumerate(not_started, 1):
        print(f"{i}. {m.title} (Game: {m.game.title})")
        print(f"   Due date: {m.due_date}")
        print(f"   Status: {m.status}")
    
    # Print completed milestones
    print(f"\n=== COMPLETED MILESTONES ({len(completed)}) ===")
    for i, m in enumerate(completed, 1):
        print(f"{i}. {m.title} (Game: {m.game.title})")
        print(f"   Completion date: {m.completion_date}")
        print(f"   Status: {m.status}")
    
    print("\n=== END OF MILESTONE STATUS ===")

if __name__ == "__main__":
    check_all_milestones()
