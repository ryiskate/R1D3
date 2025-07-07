"""
Script to check and fix milestone status in the database.
"""
import os
import django

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
        print(f"   Description: {m.description[:50]}..." if m.description and len(m.description) > 50 else f"   Description: {m.description}")
        print()

def set_milestone_status():
    """Set the correct milestone to in-progress status."""
    print("\n=== SETTING MILESTONE STATUS ===")
    
    # Ask which milestone to set as in-progress
    milestones = GameMilestone.objects.all().order_by('game__title', 'title')
    
    if not milestones:
        print("No milestones found in the database!")
        return
    
    print("Available milestones:")
    for i, m in enumerate(milestones, 1):
        print(f"{i}. {m.title} (Game: {m.game.title}, Current status: {m.status})")
    
    try:
        choice = int(input("\nEnter the number of the milestone to set as in-progress: "))
        if choice < 1 or choice > milestones.count():
            print("Invalid choice!")
            return
        
        # Get the selected milestone
        selected_milestone = milestones[choice - 1]
        
        # Set all other milestones to completed
        for m in milestones:
            if m.id != selected_milestone.id and m.status == 'in_progress':
                m.status = 'completed'
                m.completion_date = timezone.now()
                m.save()
                print(f"Set {m.title} to completed")
        
        # Set the selected milestone to in-progress
        selected_milestone.status = 'in_progress'
        selected_milestone.completion_date = None
        selected_milestone.save()
        print(f"\nSuccessfully set {selected_milestone.title} to in-progress status!")
        
    except ValueError:
        print("Please enter a valid number!")
    except Exception as e:
        print(f"Error: {str(e)}")

def fix_milestone_status(milestone_title=None, game_title=None):
    """Fix milestone status by setting the specified milestone to in-progress."""
    print("\n=== FIXING MILESTONE STATUS ===")
    
    if not milestone_title:
        print("No milestone title specified, listing all milestones...")
        list_all_milestones()
        return
    
    try:
        # Find the milestone by title (and game title if provided)
        query = {'title': milestone_title}
        if game_title:
            query['game__title'] = game_title
        
        milestone = GameMilestone.objects.filter(**query).first()
        
        if not milestone:
            print(f"No milestone found with title '{milestone_title}'")
            if game_title:
                print(f"and game '{game_title}'")
            list_all_milestones()
            return
        
        # Set all other milestones to completed
        other_milestones = GameMilestone.objects.filter(status='in_progress').exclude(id=milestone.id)
        for m in other_milestones:
            m.status = 'completed'
            m.completion_date = timezone.now()
            m.save()
            print(f"Set {m.title} to completed")
        
        # Set the selected milestone to in-progress
        milestone.status = 'in_progress'
        milestone.completion_date = None
        milestone.save()
        print(f"\nSuccessfully set {milestone.title} to in-progress status!")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    # List all milestones
    list_all_milestones()
    
    # Interactive mode
    print("\nChoose an option:")
    print("1. Set a milestone to in-progress interactively")
    print("2. Fix milestone status for 'Release First Indie Game'")
    print("3. Fix milestone status for 'Theme Park Feasibility Study'")
    print("4. Fix milestone status for 'Hardware Integration Research'")
    print("5. Exit")
    
    try:
        choice = int(input("\nEnter your choice (1-5): "))
        
        if choice == 1:
            set_milestone_status()
        elif choice == 2:
            fix_milestone_status("Release First Indie Game", "PeacefulFarm")
        elif choice == 3:
            fix_milestone_status("Theme Park Feasibility Study", "Theme Park Experience")
        elif choice == 4:
            fix_milestone_status("Hardware Integration Research", "Arcade Cabinet")
        elif choice == 5:
            print("Exiting...")
        else:
            print("Invalid choice!")
    except ValueError:
        print("Please enter a valid number!")
    except Exception as e:
        print(f"Error: {str(e)}")
