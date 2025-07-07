import os
import sys
import time
import django
import subprocess
from datetime import datetime

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'company_system.settings')
django.setup()

# Import Django models
from projects.game_models import GameMilestone, GameTask
from core.context_processors import get_phase_for_milestone

def clear_screen():
    """Clear the console screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def get_current_milestone_info():
    """Get information about the current milestone"""
    # Find milestones with in_progress status
    in_progress_milestones = GameMilestone.objects.filter(status='in_progress')
    
    if in_progress_milestones.exists():
        # Get the first in-progress milestone
        milestone = in_progress_milestones.first()
        return {
            'source': 'direct',
            'milestone': milestone,
            'title': milestone.title,
            'game': milestone.game.title,
            'status': milestone.status,
            'status_display': 'In Progress' if milestone.status == 'in_progress' else 'Completed',
            'phase_info': get_phase_for_milestone(milestone.title)
        }
    
    # If no non-completed milestones found, fall back to task-based detection
    in_progress_tasks = GameTask.objects.filter(status='in_progress')
    
    if in_progress_tasks.exists():
        # Get the first in-progress task
        task = in_progress_tasks.first()
        
        if task and task.milestone:
            # Get milestone info from the in-progress task
            milestone = task.milestone
            return {
                'source': 'task',
                'milestone': milestone,
                'title': milestone.title,
                'game': task.game.title if task.game else 'Unknown Game',
                'is_completed': milestone.is_completed,
                'status_display': 'In Progress' if not milestone.is_completed else 'Completed',
                'phase_info': get_phase_for_milestone(milestone.title),
                'task': task
            }
        elif task:
            # Task has no milestone
            return {
                'source': 'task_no_milestone',
                'task': task,
                'company_section': task.company_section
            }
    
    # No milestone or task found
    return {
        'source': 'default',
        'title': 'Release First Indie Game',
        'game': 'PeacefulFarm',
        'phase_name': 'Indie Game Development',
        'phase_type': 'indie_dev',
        'phase_order': 1
    }

def display_milestone_info(info):
    """Display milestone information in a formatted way"""
    clear_screen()
    
    print("\n" + "=" * 70)
    print(f"R1D3 MILESTONE MONITOR - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    if info['source'] == 'direct' or info['source'] == 'task':
        milestone = info['milestone']
        phase_info = info['phase_info']
        
        print(f"\nCURRENT MILESTONE: {milestone.title}")
        print("-" * 70)
        
        # Basic milestone info table
        print("+" + "-" * 20 + "+" + "-" * 47 + "+")
        print(f"| Game                | {info['game']:<45} |")
        print("+" + "-" * 20 + "+" + "-" * 47 + "+")
        print(f"| Company Phase       | {phase_info['name']:<45} |")
        print("+" + "-" * 20 + "+" + "-" * 47 + "+")
        print(f"| Phase Type          | {phase_info['phase_type']:<45} |")
        print("+" + "-" * 20 + "+" + "-" * 47 + "+")
        print(f"| Phase Order         | {phase_info['order']:<45} |")
        print("+" + "-" * 20 + "+" + "-" * 47 + "+")
        print(f"| Due Date            | {milestone.due_date if milestone.due_date else 'Not set':<45} |")
        print("+" + "-" * 20 + "+" + "-" * 47 + "+")
        status_display = "In Progress" if milestone.status == 'in_progress' else "Completed" if milestone.status == 'completed' else "Not Started"
        print(f"| Status              | {status_display:<45} |")
        print("+" + "-" * 20 + "+" + "-" * 47 + "+")
        print("+" + "-" * 20 + "+" + "-" * 47 + "+")
        
        # Get related tasks
        tasks = GameTask.objects.filter(milestone=milestone)
        
        # Tasks section
        print(f"\nRELATED TASKS ({tasks.count()})")
        print("-" * 70)
        
        if tasks.exists():
            # Table header
            print("+---+-------------------------------------+------------+------------+")
            print("| # | Task Title                          | Status      | Priority    |")
            print("+---+-------------------------------------+------------+------------+")
            
            for i, task in enumerate(tasks[:5], 1):  # Show only first 5 tasks
                title = task.title[:35] + '...' if len(task.title) > 35 else task.title.ljust(35)
                print(f"| {i:<1} | {title} | {task.status.ljust(10)} | {task.priority.ljust(10)} |")
            
            print("+---+-------------------------------------+------------+------------+")
            
            if tasks.count() > 5:
                print(f"  ... and {tasks.count() - 5} more tasks not shown")
        else:
            print("  No tasks associated with this milestone")
    
    elif info['source'] == 'task_no_milestone':
        task = info['task']
        print("\nWARNING: In-progress task has no milestone")
        print("-" * 70)
        print(f"Task: {task.title}")
        print(f"Company Section: {task.company_section}")
    
    else:  # Default
        print("\nWARNING: No in-progress milestone or task found")
        print("-" * 70)
        print(f"Using default milestone: '{info['title']}'")
        print(f"Default phase: {info['phase_name']} (Type: {info['phase_type']})")    
    
    print("\n" + "=" * 70)
    print("Press Ctrl+C to exit the monitor")
    print("=" * 70)

def monitor_milestone_changes():
    """Monitor for changes in the current milestone"""
    print("Starting R1D3 Milestone Monitor...")
    
    last_info = None
    last_milestone_title = None
    
    try:
        while True:
            current_info = get_current_milestone_info()
            current_milestone_title = current_info.get('title', None)
            
            # Display if it's the first run or if the milestone has changed
            if last_info is None or current_milestone_title != last_milestone_title:
                display_milestone_info(current_info)
                last_info = current_info
                last_milestone_title = current_milestone_title
            
            # Check every 2 seconds
            time.sleep(2)
    
    except KeyboardInterrupt:
        print("\nExiting R1D3 Milestone Monitor...")
        sys.exit(0)

if __name__ == "__main__":
    monitor_milestone_changes()
