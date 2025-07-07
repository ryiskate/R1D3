from django.core.management.base import BaseCommand
from django.utils import timezone
from projects.game_models import GameMilestone, GameProject
import datetime

class Command(BaseCommand):
    help = 'Creates test milestones for each company phase'

    def handle(self, *args, **options):
        # Make sure we have at least one game project
        game_project, created = GameProject.objects.get_or_create(
            title="PeacefulFarm",
            defaults={
                'description': 'A relaxing farming simulation game',
                'start_date': timezone.now().date(),
                'status': 'production',
                'genre': 'simulation',
                'platforms': 'pc'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created game project: {game_project.title}'))
        else:
            self.stdout.write(f'Using existing game project: {game_project.title}')
            
        # Create a second game project for arcade games
        arcade_project, created = GameProject.objects.get_or_create(
            title="Arcade Cabinet",
            defaults={
                'description': 'Custom arcade cabinet with multiple games',
                'start_date': timezone.now().date(),
                'status': 'pre_production',
                'genre': 'multi',
                'platforms': 'multi'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created game project: {arcade_project.title}'))
        else:
            self.stdout.write(f'Using existing game project: {arcade_project.title}')
            
        # Create a third game project for theme park attractions
        theme_park_project, created = GameProject.objects.get_or_create(
            title="Theme Park Experience",
            defaults={
                'description': 'Interactive theme park attraction',
                'start_date': timezone.now().date(),
                'status': 'concept',
                'genre': 'simulation',
                'platforms': 'multi'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created game project: {theme_park_project.title}'))
        else:
            self.stdout.write(f'Using existing game project: {theme_park_project.title}')

        # First, reset all existing milestones to not completed
        GameMilestone.objects.all().update(is_completed=False)
        
        # Define milestones for each phase
        milestones = [
            # Phase 1: Indie Game Development
            {
                'title': 'Complete Game Development Course',
                'game': game_project,
                'due_date': timezone.now().date() - datetime.timedelta(days=60),
                'is_completed': True,
                'completion_date': timezone.now().date() - datetime.timedelta(days=60)
            },
            {
                'title': 'Release First Indie Game',
                'game': game_project,
                'due_date': timezone.now().date() + datetime.timedelta(days=30),
                'is_completed': False
            },
            {
                'title': 'Build Game Portfolio',
                'game': game_project,
                'due_date': timezone.now().date() + datetime.timedelta(days=90),
                'is_completed': False
            },
            
            # Phase 2: Arcade Machine Development
            {
                'title': 'Hardware Integration Research',
                'game': arcade_project,
                'due_date': timezone.now().date() + datetime.timedelta(days=15),
                'is_completed': False
            },
            {
                'title': 'Prototype First Arcade Cabinet',
                'game': arcade_project,
                'due_date': timezone.now().date() + datetime.timedelta(days=75),
                'is_completed': False
            },
            
            # Phase 3: Theme Park Attractions
            {
                'title': 'Theme Park Feasibility Study',
                'game': theme_park_project,
                'due_date': timezone.now().date() + datetime.timedelta(days=120),
                'is_completed': False
            }
        ]

        # Create or update milestones
        for milestone_data in milestones:
            milestone, created = GameMilestone.objects.update_or_create(
                title=milestone_data['title'],
                game=milestone_data['game'],
                defaults={
                    'due_date': milestone_data['due_date'],
                    'is_completed': milestone_data.get('is_completed', False),
                    'completion_date': milestone_data.get('completion_date', None)
                }
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created milestone: {milestone.title}'))
            else:
                self.stdout.write(f'Updated milestone: {milestone.title}')
