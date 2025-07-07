import os
import django
import sys

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'company_system.settings')
django.setup()

from projects.game_models import GameMilestone

print('Debugging milestone status property...')

try:
    print('Trying to access all milestones:')
    all_milestones = GameMilestone.objects.all()
    print(f'Found {all_milestones.count()} total milestones')
    
    for milestone in all_milestones:
        print(f'Milestone: {milestone.title}, is_completed: {milestone.is_completed}')
        try:
            print(f'  Status via property: {milestone.status}')
        except Exception as e:
            print(f'  Error accessing status property: {e}')
    
    print('\nTrying to filter by status:')
    try:
        in_progress = GameMilestone.objects.filter(status='in_progress')
        print(f'Found {in_progress.count()} in-progress milestones')
    except Exception as e:
        print(f'Error filtering by status: {e}')
        
except Exception as e:
    print(f'Error: {e}')
