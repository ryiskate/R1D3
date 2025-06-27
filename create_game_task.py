import os
import django
import sys

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'company_system.settings')
django.setup()

from django.contrib.auth.models import User
from projects.task_models import GameDevelopmentTask
from datetime import date, timedelta

# Find a user to assign tasks to
try:
    user = User.objects.get(username='ricardoide')
    print(f"Found user: {user.username}")
except User.DoesNotExist:
    user = User.objects.first()
    if user:
        print(f"Using user: {user.username}")
    else:
        print("No users found in the system.")
        sys.exit(1)

# Create a Game Development task
game_task = GameDevelopmentTask.objects.create(
    title="Test Game Development Task",
    description="This is a test task for the Game Development section",
    status="to_do",
    priority="medium",
    created_by=user,
    assigned_to=user,
    due_date=date.today() + timedelta(days=7),
    platform="PC"
)
print(f"Created Game Development task: {game_task.id} - {game_task.title}")
