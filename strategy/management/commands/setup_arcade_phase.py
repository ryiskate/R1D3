from django.core.management.base import BaseCommand
from strategy.models import StrategyPhase
from projects.game_models import GameMilestone, GameProject
from django.utils import timezone

class Command(BaseCommand):
    help = 'Sets up the Arcade Machine Development phase and Hardware Integration Research milestone'

    def handle(self, *args, **options):
        # Reset all phases to not current
        StrategyPhase.objects.all().update(is_current=False)
        
        # Create or update the Arcade phase
        arcade_phase, created = StrategyPhase.objects.update_or_create(
            phase_type='arcade',
            defaults={
                'name': 'Arcade Machine Development',
                'description': 'Expanding into physical gaming experiences through arcade machine development.',
                'order': 2,
                'start_year': timezone.now().year,
                'end_year': timezone.now().year + 2,
                'is_current': True,
                'is_completed': False
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created Arcade phase: {arcade_phase}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Updated Arcade phase: {arcade_phase}'))
        
        # Create or get a game project for the arcade phase
        game_project, created = GameProject.objects.get_or_create(
            title='Arcade Cabinet',
            defaults={
                'description': 'Our first arcade cabinet project',
                'status': 'in_progress'
            }
        )
        
        # Create or update the Hardware Integration Research milestone
        milestone, created = GameMilestone.objects.update_or_create(
            game=game_project,
            title='Hardware Integration Research',
            defaults={
                'description': 'Complete research on hardware integration for arcade cabinets',
                'due_date': timezone.now().date() + timezone.timedelta(days=60),
                'is_completed': False
            }
        )
        
        # Mark all other milestones as completed
        GameMilestone.objects.exclude(id=milestone.id).update(is_completed=True)
        
        self.stdout.write(self.style.SUCCESS(f'Set up Hardware Integration Research milestone as the current active milestone'))
