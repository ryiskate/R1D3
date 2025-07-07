import os
import django
import sys

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'company_system.settings')
django.setup()

from projects.game_models import GameMilestone

print('Checking current milestone status...')

# Check milestone data
print("\nMilestone data in database:")
milestones = GameMilestone.objects.all()
print(f"Total milestones: {milestones.count()}")

# Check in-progress milestones
in_progress = GameMilestone.objects.filter(status='in_progress')
print(f"\nIn-progress milestones: {in_progress.count()}")
for m in in_progress:
    print(f"  - {m.title} (Game: {m.game.title})")

# Check completed milestones
completed = GameMilestone.objects.filter(status='completed')
print(f"\nCompleted milestones: {completed.count()}")
for m in completed:
    print(f"  - {m.title} (Game: {m.game.title})")

# Check not_started milestones
not_started = GameMilestone.objects.filter(status='not_started')
print(f"\nNot started milestones: {not_started.count()}")
for m in not_started:
    print(f"  - {m.title} (Game: {m.game.title})")
