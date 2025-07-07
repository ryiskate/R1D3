from django.core.management.base import BaseCommand, CommandError
from projects.game_models import GameMilestone, GameTask
from django.utils import timezone

class Command(BaseCommand):
    help = 'Set a milestone as the current milestone by creating an in-progress task for it'

    def add_arguments(self, parser):
        parser.add_argument('--milestone', type=str, required=True, help='Title of the milestone to set as current')
        parser.add_argument('--clear-others', action='store_true', help='Clear in-progress status from all other tasks')
        parser.add_argument('--phase', type=str, choices=['indie_dev', 'arcade', 'theme_park'], 
                          default='indie_dev', help='Company phase for the milestone')

    def handle(self, *args, **options):
        milestone_title = options['milestone']
        clear_others = options['clear_others']
        phase = options['phase']
        
        # Map phase to company_section
        company_section_map = {
            'indie_dev': 'game_development',
            'arcade': 'arcade',
            'theme_park': 'theme_park'
        }
        company_section = company_section_map.get(phase, 'game_development')
        
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
            
            # Reset status for all milestones in the same game
            other_milestones = GameMilestone.objects.filter(game=milestone.game).exclude(id=milestone.id)
            for other in other_milestones:
                if other.status == 'in_progress':
                    # Mark all other in-progress milestones as completed to ensure only one is 'in progress'
                    other.status = 'completed'
                    other.completion_date = timezone.now().date()
                    other.save()
                    self.stdout.write(f'Marked milestone "{other.title}" as completed')
            
            # Set the target milestone as in progress
            milestone.status = 'in_progress'
            milestone.completion_date = None
            milestone.save()
            
            # If clearing other in-progress tasks
            if clear_others:
                in_progress_tasks = GameTask.objects.filter(status='in_progress')
                count = in_progress_tasks.count()
                if count > 0:
                    in_progress_tasks.update(status='to_do')
                    self.stdout.write(self.style.SUCCESS(f'Cleared in-progress status from {count} task(s)'))
            
            # Create a new task for this milestone with in-progress status
            task_title = f"Implement {milestone.title}"
            
            # Check if a task already exists for this milestone
            existing_task = GameTask.objects.filter(milestone=milestone, title=task_title).first()
            
            if existing_task:
                # Update existing task to in-progress
                existing_task.status = 'in_progress'
                existing_task.company_section = company_section
                existing_task.save()
                self.stdout.write(self.style.SUCCESS(f'Updated existing task "{task_title}" to in-progress'))
            else:
                # Create new task
                new_task = GameTask.objects.create(
                    title=task_title,
                    milestone=milestone,
                    game=milestone.game,
                    status='in_progress',
                    company_section=company_section
                )
                self.stdout.write(self.style.SUCCESS(f'Created new in-progress task "{task_title}"'))
            
            self.stdout.write(self.style.SUCCESS(
                f'Successfully set milestone "{milestone.title}" as the current milestone for {phase} phase'
            ))
            
        except Exception as e:
            raise CommandError(f'Error setting current milestone: {str(e)}')
