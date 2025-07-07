from django.core.management.base import BaseCommand, CommandError
from projects.game_models import GameMilestone
from django.db import connection
from django.core.cache import cache

class Command(BaseCommand):
    help = 'Sets a specific milestone as the active one by marking others as completed'

    def add_arguments(self, parser):
        parser.add_argument('milestone_title', type=str, help='Title of the milestone to set as active')

    def handle(self, *args, **options):
        milestone_title = options['milestone_title']
        
        try:
            # Clear Django's cache to ensure fresh data
            cache.clear()
            
            # Reset connection to ensure fresh database state
            connection.close()
            
            # Find the milestone with the given title
            target_milestone = GameMilestone.objects.filter(title=milestone_title).first()
            
            if not target_milestone:
                self.stdout.write(self.style.ERROR(f'Milestone with title "{milestone_title}" not found'))
                self.stdout.write('Available milestones:')
                for milestone in GameMilestone.objects.all():
                    self.stdout.write(f'- {milestone.title}')
                return
            
            # Mark all milestones as completed except the target one
            GameMilestone.objects.exclude(id=target_milestone.id).update(is_completed=True)
            
            # Make sure the target milestone is not completed and update its due date
            # to ensure it's the earliest due date (making it the active milestone)
            from django.utils import timezone
            target_milestone.is_completed = False
            target_milestone.due_date = timezone.now().date() + timezone.timedelta(days=1)
            target_milestone.save()
            
            # Django auto-commits transactions, no need to manually commit
            # Just make sure we're not in an atomic block
            connection.close()
            
            self.stdout.write(self.style.SUCCESS(f'Successfully set "{milestone_title}" as the active milestone'))
            
            # Show the current active milestone
            self.stdout.write('\nCurrent active milestone:')
            self.stdout.write(f'Title: {target_milestone.title}')
            self.stdout.write(f'Game: {target_milestone.game.title}')
            self.stdout.write(f'Due date: {target_milestone.due_date}')
            
        except Exception as e:
            raise CommandError(f'Error setting active milestone: {str(e)}')
