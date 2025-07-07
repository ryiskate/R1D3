from django.core.management.base import BaseCommand
from django.utils import timezone
from projects.game_models import GameProject, GameMilestone, GameTask
import random

class Command(BaseCommand):
    help = 'Creates a test task with "in_progress" status for a specific milestone'

    def add_arguments(self, parser):
        parser.add_argument('--milestone', type=str, help='Milestone title to set as in progress')
        parser.add_argument('--phase', type=str, help='Phase type (indie_dev, arcade, theme_park)')

    def handle(self, *args, **options):
        # Clear any existing in-progress tasks
        GameTask.objects.filter(status='in_progress').update(status='to_do')
        self.stdout.write(self.style.SUCCESS('Cleared existing in-progress tasks'))
        
        milestone_title = options.get('milestone')
        phase_type = options.get('phase')
        
        # Default milestone titles for each phase
        phase_milestones = {
            'indie_dev': ['Release First Indie Game', 'Complete Game Development Course', 'Build Game Portfolio'],
            'arcade': ['Open First Arcade Location', 'Prototype First Arcade Cabinet', 'Launch First Arcade Location'],
            'theme_park': ['Theme Park Feasibility Study', 'Attraction Prototype', 'First Attraction Launch']
        }
        
        # If no milestone specified, use a default based on phase or random if no phase
        if not milestone_title:
            if phase_type and phase_type in phase_milestones:
                milestone_title = random.choice(phase_milestones[phase_type])
            else:
                # Pick a random phase and milestone
                phase_type = random.choice(list(phase_milestones.keys()))
                milestone_title = random.choice(phase_milestones[phase_type])
        
        # Try to find the milestone or create it
        milestone = None
        try:
            milestone = GameMilestone.objects.filter(title__icontains=milestone_title).first()
            
            if not milestone:
                # Create a game project if needed
                game, created = GameProject.objects.get_or_create(
                    title=f"Test Game for {milestone_title}",
                    defaults={
                        'description': 'Test game project for milestone testing',
                        'start_date': timezone.now().date(),
                        'status': 'production'
                    }
                )
                
                # Create the milestone
                milestone = GameMilestone.objects.create(
                    game=game,
                    title=milestone_title,
                    description=f'Test milestone for {milestone_title}',
                    due_date=timezone.now().date() + timezone.timedelta(days=30),
                    is_completed=False
                )
                self.stdout.write(self.style.SUCCESS(f'Created new milestone: {milestone.title}'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Found existing milestone: {milestone.title}'))
                
            # Create a task for this milestone with in_progress status
            task = GameTask.objects.create(
                game=milestone.game,
                milestone=milestone,
                title=f"Implement {milestone.title}",
                description=f"Implementation task for {milestone.title}",
                status='in_progress',
                priority='high',
                due_date=timezone.now().date() + timezone.timedelta(days=7),
                company_section='arcade' if 'arcade' in phase_type.lower() else 'game_development'
            )
            
            self.stdout.write(self.style.SUCCESS(f'Created in-progress task: {task.title}'))
            self.stdout.write(self.style.SUCCESS(f'Associated with milestone: {milestone.title}'))
            self.stdout.write(self.style.SUCCESS(f'Company section: {task.company_section}'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating in-progress task: {str(e)}'))
