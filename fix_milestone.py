"""
Script to check and fix the current milestone status.
"""
import os
import django
import sys

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'company_system.settings')
django.setup()

# Import models
from projects.game_models import GameMilestone, GameTask
from django.utils import timezone

def list_all_milestones():
    """List all milestones in the database."""
    print("\n=== ALL MILESTONES IN DATABASE ===")
    
    milestones = GameMilestone.objects.all().order_by('game__title', 'title')
    
    if not milestones:
        print("No milestones found in the database!")
        return
    
    print(f"Found {milestones.count()} milestones in total:")
    
    for i, m in enumerate(milestones, 1):
        print(f"{i}. {m.title} (Game: {m.game.title})")
        print(f"   Status: {m.status}")
        print(f"   Due date: {m.due_date}")
        print()

def set_specific_milestone(milestone_id=None):
    """Set a specific milestone as in-progress and mark others as completed."""
    milestones = GameMilestone.objects.all()
    
    if milestone_id:
        try:
            target_milestone = GameMilestone.objects.get(id=milestone_id)
        except GameMilestone.DoesNotExist:
            print(f"Error: No milestone with ID {milestone_id}")
            return
    else:
        # Default to the first milestone if no ID provided
        if not milestones.exists():
            print("No milestones found in the database!")
            return
        target_milestone = milestones.first()
    
    print(f"\nSetting milestone '{target_milestone.title}' as in-progress...")
    
    # Set all other milestones to completed
    for m in milestones:
        if m.id != target_milestone.id:
            if m.status == 'in_progress':
                m.status = 'completed'
                if not m.completion_date:
                    m.completion_date = timezone.now()
                m.save()
                print(f"Set '{m.title}' to completed")
    
    # Set the target milestone to in-progress
    target_milestone.status = 'in_progress'
    target_milestone.completion_date = None
    target_milestone.save()
    print(f"Set '{target_milestone.title}' to in-progress")
    
    print("\nCurrent milestone status:")
    list_all_milestones()

if __name__ == "__main__":
    # List all milestones first
    list_all_milestones()
    
    # Check if a milestone ID was provided as an argument
    if len(sys.argv) > 1:
        try:
            milestone_id = int(sys.argv[1])
            set_specific_milestone(milestone_id)
        except ValueError:
            print("Error: Milestone ID must be a number")
    else:
        # If no ID provided, ask for input
        try:
            choice = input("\nEnter milestone ID to set as in-progress (or press Enter to list milestones): ")
            if choice.strip():
                set_specific_milestone(int(choice))
            else:
                # Just list milestones again
                pass
        except ValueError:
            print("Error: Please enter a valid number")
