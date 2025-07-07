import os
import django
import sys

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'company_system.settings')
django.setup()

from projects.game_models import GameMilestone
from django.db import connection

print('Debugging milestone data...')

# Check the database schema
with connection.cursor() as cursor:
    cursor.execute("PRAGMA table_info(projects_gamemilestone)")
    columns = cursor.fetchall()
    print("\nTable schema for projects_gamemilestone:")
    for col in columns:
        print(f"  {col[1]} ({col[2]})")

# Check milestone data
print("\nMilestone data in database:")
milestones = GameMilestone.objects.all()
print(f"Total milestones: {milestones.count()}")

for milestone in milestones:
    print(f"\nMilestone ID: {milestone.id}")
    print(f"  Title: {milestone.title}")
    print(f"  Game: {milestone.game.title}")
    print(f"  is_completed: {milestone.is_completed}")
    print(f"  status: {milestone.status}")
    print(f"  completion_date: {milestone.completion_date}")

# Try filtering by status
print("\nTrying to filter by status:")
try:
    in_progress = GameMilestone.objects.filter(status='in_progress')
    print(f"Found {in_progress.count()} in-progress milestones:")
    for m in in_progress:
        print(f"  - {m.title}")
except Exception as e:
    print(f"Error filtering by status: {e}")

# Check for any active milestone
print("\nChecking for active milestone:")
try:
    not_completed = GameMilestone.objects.filter(is_completed=False)
    print(f"Found {not_completed.count()} non-completed milestones:")
    for m in not_completed:
        print(f"  - {m.title} (status: {m.status})")
except Exception as e:
    print(f"Error filtering by is_completed: {e}")
