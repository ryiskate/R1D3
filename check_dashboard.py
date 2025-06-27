import os
import django
import sys

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'company_system.settings')
django.setup()

# Import models after Django setup
from django.contrib.auth.models import User
from projects.game_models import GameTask
from projects.task_models import (
    R1D3Task, GameDevelopmentTask, EducationTask,
    SocialMediaTask, ArcadeTask, ThemeParkTask
)

# Check if admin user exists
admin_user = User.objects.filter(username='admin').first()
if not admin_user:
    print("Creating admin user...")
    admin_user = User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
else:
    print(f"Admin user exists: {admin_user}")

# Print task counts
print(f"GameTask count: {GameTask.objects.count()}")
print(f"R1D3Task count: {R1D3Task.objects.count()}")
print(f"GameDevelopmentTask count: {GameDevelopmentTask.objects.count()}")
print(f"EducationTask count: {EducationTask.objects.count()}")
print(f"SocialMediaTask count: {SocialMediaTask.objects.count()}")
print(f"ArcadeTask count: {ArcadeTask.objects.count()}")
print(f"ThemeParkTask count: {ThemeParkTask.objects.count()}")

# Print details of GameTask objects
print("\nGameTask objects:")
for task in GameTask.objects.all():
    print(f"- {task.title} (Section: {task.company_section})")

# Print details of R1D3Task objects
print("\nR1D3Task objects:")
for task in R1D3Task.objects.all():
    print(f"- {task.title}")

print("\nDone!")
