"""
Debug script to check the current state of milestones and tasks in the database
"""
import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'company_system.settings')
django.setup()

from projects.game_models import GameTask, GameMilestone
from django.db.models import F

def debug_milestone_data():
    print("=" * 50)
    print("DEBUGGING MILESTONE DATA")
    print("=" * 50)
    
    # Check in-progress tasks
    print("\n1. CHECKING IN-PROGRESS TASKS:")
    in_progress_tasks = GameTask.objects.filter(status='in_progress')
    if in_progress_tasks.exists():
        print(f"Found {in_progress_tasks.count()} in-progress tasks:")
        for task in in_progress_tasks:
            print(f"  - Task: {task.title}")
            print(f"    Status: {task.status}")
            print(f"    Game: {task.game.title if task.game else 'None'}")
            print(f"    Milestone: {task.milestone.title if task.milestone else 'None'}")
            print(f"    Company Section: {task.company_section}")
    else:
        print("No in-progress tasks found.")
    
    # Check all milestones
    print("\n2. CHECKING ALL GAME MILESTONES:")
    milestones = GameMilestone.objects.all()
    if milestones.exists():
        print(f"Found {milestones.count()} game milestones:")
        for milestone in milestones:
            print(f"  - Milestone: {milestone.title}")
            print(f"    Game: {milestone.game.title if milestone.game else 'None'}")
            print(f"    Completed: {milestone.is_completed}")
            
            # Check tasks for this milestone
            tasks = GameTask.objects.filter(milestone=milestone)
            if tasks.exists():
                print(f"    Tasks ({tasks.count()}):")
                for task in tasks:
                    print(f"      - {task.title} (Status: {task.status})")
            else:
                print("    No tasks associated with this milestone.")
    else:
        print("No game milestones found.")
    
    print("\n3. CURRENT MILESTONE DETERMINATION LOGIC:")
    try:
        from core.context_processors import get_phase_for_milestone
        
        print("Checking in-progress tasks for milestone determination...")
        in_progress_task = GameTask.objects.filter(status='in_progress').first()
        
        if in_progress_task and in_progress_task.milestone:
            milestone_title = in_progress_task.milestone.title
            print(f"Found in-progress task with milestone: {milestone_title}")
            
            phase_info = get_phase_for_milestone(milestone_title)
            print(f"Phase determined from milestone: {phase_info['name']} (Type: {phase_info['phase_type']})")
            
            # Generate the background style that would be used
            if phase_info['phase_type'] == 'indie_dev':
                bg_style = "background: linear-gradient(135deg, #4e73df 0%, #224abe 100%);"
            elif phase_info['phase_type'] == 'arcade':
                bg_style = "background: linear-gradient(135deg, #1cc88a 0%, #13855c 100%);"
            elif phase_info['phase_type'] == 'theme_park':
                bg_style = "background: linear-gradient(135deg, #f6c23e 0%, #dda20a 100%);"
            else:
                bg_style = "background: linear-gradient(135deg, #4e73df 0%, #224abe 100%);"
                
            print(f"Background style would be: {bg_style}")
        else:
            print("No in-progress task with milestone found.")
    except Exception as e:
        print(f"Error in milestone determination logic: {str(e)}")
    
    print("=" * 50)
    print("END OF DEBUGGING")
    print("=" * 50)

if __name__ == "__main__":
    debug_milestone_data()
