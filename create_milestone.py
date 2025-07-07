from django.core.management import setup_environ
import os
import sys
import datetime

# Add the project directory to the Python path
sys.path.append('e:\\SistemaR1D3')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'company_system.settings')

# Import Django and setup
import django
django.setup()

# Now we can import our models
from projects.game_models import GameProject, GameMilestone
from django.utils import timezone

# Get the first game
game = GameProject.objects.first()
if game:
    # Create a milestone
    milestone = GameMilestone.objects.create(
        game=game,
        title='Alpha Release',
        description='First playable alpha version',
        due_date=timezone.now().date() + datetime.timedelta(days=30),
        is_completed=False
    )
    print(f'Created milestone for game: {game.title}')
    print(f'Milestone: {milestone.title}, Due: {milestone.due_date}')
else:
    print('No games found in database')

# Check if the milestone was created
print(f'Total milestones: {GameMilestone.objects.count()}')
