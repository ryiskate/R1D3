"""
Test script to check the current active milestone in the database.
"""
import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'company_system.settings')
django.setup()

# Import models
from projects.game_models import GameMilestone
from django.utils import timezone

def check_active_milestone():
    """Check which milestone is currently active in the database."""
    print("\n=== CURRENT MILESTONE STATUS ===")
    
    # Get all milestones ordered by due date
    milestones = GameMilestone.objects.filter(status__in=['not_started', 'in_progress']).order_by('due_date')
    
    if not milestones:
        print("No active milestones found!")
        return
    
    print(f"Found {milestones.count()} active milestones:")
    
    # Print all milestones with their details
    for i, m in enumerate(milestones):
        print(f"{i+1}. {m.title} (Due: {m.due_date}, Status: {m.status})")
        
    # The first one should be the active milestone
    active = milestones.first()
    print(f"\nCURRENT ACTIVE MILESTONE: {active.title}")
    print(f"Due date: {active.due_date}")
    print(f"Status: {active.status}")
    print(f"Game: {active.game.title if active.game else 'None'}")
    
    # Check for any issues that might prevent it from showing correctly
    today = timezone.now().date()
    if active.due_date > today:
        print(f"WARNING: Due date is in the future ({active.due_date}), which might affect display logic")
    
    print("\n=== END OF MILESTONE STATUS ===")

if __name__ == "__main__":
    check_active_milestone()
