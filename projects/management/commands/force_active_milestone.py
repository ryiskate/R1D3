import datetime
import time
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import connection, transaction
from django.core.cache import cache
from projects.game_models import GameMilestone, GameProject

class Command(BaseCommand):
    help = 'Force a specific milestone to be the active one by adjusting due dates'

    def add_arguments(self, parser):
        parser.add_argument('milestone_title', type=str, help='Title of the milestone to set as active')

    def handle(self, *args, **options):
        milestone_title = options['milestone_title']
        print(milestone_title)  # Debug output
        
        # Clear Django's cache to ensure fresh data
        cache.clear()
        
        # Reset database connection to ensure fresh queries
        connection.close()
        
        # Find the milestone with the given title
        target_milestone = GameMilestone.objects.filter(title=milestone_title).first()
        
        if not target_milestone:
            self.stdout.write(self.style.ERROR(f'Milestone with title "{milestone_title}" not found'))
            self.stdout.write('Available milestones:')
            for milestone in GameMilestone.objects.all():
                self.stdout.write(f'- {milestone.title}')
            return
        
        # Set the target milestone as not completed
        target_milestone.is_completed = False
        
        # Set the target milestone to be due today
        target_milestone.due_date = timezone.now().date()
        target_milestone.is_completed = False
        target_milestone.save()
        
        # Print debug info
        print(f"Setting milestone '{milestone_title}' as active with due date {target_milestone.due_date}")
        
        # Force commit the transaction
        connection.commit()
        
        # Set all other milestones to have a later due date and mark as not completed
        other_milestones = GameMilestone.objects.exclude(id=target_milestone.id)
        
        # Set all other milestones to have a later due date
        for i, milestone in enumerate(other_milestones):
            milestone.due_date = timezone.now().date() + datetime.timedelta(days=i+2)
            milestone.is_completed = False  # Make sure all milestones are not completed
            milestone.save()
            
        # Force database to commit changes
        connection.commit()
        
        self.stdout.write(self.style.SUCCESS(f'Successfully forced "{milestone_title}" to be the active milestone'))
        self.stdout.write(f'Due date set to: {target_milestone.due_date}')
        
        # Show all milestones and their due dates
        self.stdout.write('\nAll milestones:')
        for m in GameMilestone.objects.all().order_by('due_date'):
            status = "ACTIVE" if m.id == target_milestone.id else ""
            self.stdout.write(f'- {m.title} (Due: {m.due_date}) {status}')
