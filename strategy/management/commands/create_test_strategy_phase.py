from django.core.management.base import BaseCommand
from strategy.models import StrategyPhase
from django.utils import timezone

class Command(BaseCommand):
    help = 'Creates a test strategy phase for development purposes'

    def handle(self, *args, **options):
        # Check if we already have a strategy phase with indie_dev type
        existing_phase = StrategyPhase.objects.filter(phase_type='indie_dev').first()
        
        if existing_phase:
            self.stdout.write(self.style.WARNING(f'Strategy phase already exists: {existing_phase}'))
            # Update it to be current
            existing_phase.is_current = True
            existing_phase.is_completed = False
            existing_phase.save()
            self.stdout.write(self.style.SUCCESS(f'Updated existing phase: {existing_phase}'))
            return
            
        # Create a new strategy phase
        current_year = timezone.now().year
        phase = StrategyPhase.objects.create(
            name='Indie Game Development Phase',
            phase_type='indie_dev',
            description='Building a foundation in game development through education and indie projects.',
            order=1,
            start_year=current_year,
            end_year=current_year + 3,
            is_current=True,
            is_completed=False
        )
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created strategy phase: {phase}'))
