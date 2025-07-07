from django.core.management.base import BaseCommand, CommandError
from projects.game_models import GameMilestone
from core.context_processors import get_phase_for_milestone

class Command(BaseCommand):
    help = 'Set a milestone status to in_progress or completed'

    def add_arguments(self, parser):
        parser.add_argument('--milestone', type=str, help='Title of the milestone to update')
        parser.add_argument('--status', type=str, choices=['in_progress', 'completed'], 
                            help='New status for the milestone')
        parser.add_argument('--clear-other', action='store_true', 
                            help='Mark all other in-progress milestones as completed')

    def handle(self, *args, **options):
        milestone_title = options['milestone']
        new_status = options['status']
        clear_other = options['clear_other']
        
        if not milestone_title or not new_status:
            raise CommandError('Both --milestone and --status are required')
            
        # Find the milestone by title
        try:
            milestones = GameMilestone.objects.filter(title__icontains=milestone_title)
            
            if not milestones.exists():
                self.stdout.write(self.style.ERROR(f'No milestone found with title containing "{milestone_title}"'))
                return
                
            if milestones.count() > 1:
                self.stdout.write(self.style.WARNING(f'Found multiple milestones matching "{milestone_title}":'))
                for i, m in enumerate(milestones):
                    self.stdout.write(f'  {i+1}. {m.title} ({m.game.title})')
                self.stdout.write(self.style.WARNING('Please provide a more specific milestone title'))
                return
                
            milestone = milestones.first()
            
            # If setting to in_progress, ALWAYS clear ALL other in-progress milestones
            # regardless of phase type to ensure only one milestone is in progress at a time
            if new_status == 'in_progress':
                # Clear ALL other in-progress milestones except the current one
                other_in_progress = GameMilestone.objects.filter(status='in_progress').exclude(id=milestone.id)
                count = other_in_progress.count()
                if count > 0:
                    self.stdout.write(self.style.WARNING(f'Found {count} existing in-progress milestones'))
                    for other in other_in_progress:
                        self.stdout.write(f'  - Marking "{other.title}" as completed')
                        other.status = 'completed'
                        other.save()
                    self.stdout.write(self.style.SUCCESS(f'Marked all {count} existing in-progress milestone(s) as completed'))
            
            # Update the milestone status directly
            milestone.status = new_status  # This will update is_completed via the property
            milestone.save()
            
            self.stdout.write(self.style.SUCCESS(f'Successfully updated milestone "{milestone.title}" status to {new_status}'))
            
        except Exception as e:
            raise CommandError(f'Error updating milestone status: {str(e)}')
