from django.core.management.base import BaseCommand
from projects.game_models import GameProject, GameMilestone
from django.utils import timezone
import datetime

class Command(BaseCommand):
    help = 'Creates a test milestone for the first game in the database'

    def handle(self, *args, **options):
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
            self.stdout.write(self.style.SUCCESS(f'Created milestone for game: {game.title}'))
            self.stdout.write(self.style.SUCCESS(f'Milestone: {milestone.title}, Due: {milestone.due_date}'))
        else:
            self.stdout.write(self.style.ERROR('No games found in database'))

        # Check if the milestone was created
        self.stdout.write(self.style.SUCCESS(f'Total milestones: {GameMilestone.objects.count()}'))
