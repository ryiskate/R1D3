from django.core.management.base import BaseCommand
from projects.game_models import GameProject, GameMilestone
from django.utils import timezone
import datetime

class Command(BaseCommand):
    help = 'Creates a "Release First Indie Game" milestone marked as In Progress'

    def handle(self, *args, **options):
        # Get the first game
        game = GameProject.objects.first()
        if game:
            # Create the "Release First Indie Game" milestone
            milestone = GameMilestone.objects.create(
                game=game,
                title='Release First Indie Game',
                description='Develop and release our first indie game on Steam',
                due_date=timezone.now().date() + datetime.timedelta(days=60),
                is_completed=False
            )
            self.stdout.write(self.style.SUCCESS(f'Created "Release First Indie Game" milestone for game: {game.title}'))
            
            # Delete the Alpha Release milestone if it exists
            try:
                alpha = GameMilestone.objects.get(title='Alpha Release')
                alpha.delete()
                self.stdout.write(self.style.SUCCESS('Deleted "Alpha Release" milestone'))
            except GameMilestone.DoesNotExist:
                pass
        else:
            self.stdout.write(self.style.ERROR('No games found in database'))

        # Check milestones
        self.stdout.write(self.style.SUCCESS(f'Current milestones:'))
        for m in GameMilestone.objects.all():
            self.stdout.write(f'- {m.title} (Game: {m.game.title}, Completed: {m.is_completed})')
