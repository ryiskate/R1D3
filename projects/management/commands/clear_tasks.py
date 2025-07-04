from django.core.management.base import BaseCommand
from projects.task_models import GameDevelopmentTask, EducationTask, SocialMediaTask, ArcadeTask, ThemeParkTask, R1D3Task

class Command(BaseCommand):
    help = 'Clears all tasks from the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--type',
            type=str,
            help='Type of tasks to clear: game, education, social, arcade, theme_park, r1d3, or all',
        )

    def handle(self, *args, **options):
        task_type = options.get('type', 'all')
        
        if task_type == 'game' or task_type == 'all':
            count = GameDevelopmentTask.objects.count()
            GameDevelopmentTask.objects.all().delete()
            self.stdout.write(self.style.SUCCESS(f'Successfully deleted {count} game development tasks'))
            
        if task_type == 'education' or task_type == 'all':
            count = EducationTask.objects.count()
            EducationTask.objects.all().delete()
            self.stdout.write(self.style.SUCCESS(f'Successfully deleted {count} education tasks'))
            
        if task_type == 'social' or task_type == 'all':
            count = SocialMediaTask.objects.count()
            SocialMediaTask.objects.all().delete()
            self.stdout.write(self.style.SUCCESS(f'Successfully deleted {count} social media tasks'))
            
        if task_type == 'arcade' or task_type == 'all':
            count = ArcadeTask.objects.count()
            ArcadeTask.objects.all().delete()
            self.stdout.write(self.style.SUCCESS(f'Successfully deleted {count} arcade tasks'))
            
        if task_type == 'theme_park' or task_type == 'all':
            count = ThemeParkTask.objects.count()
            ThemeParkTask.objects.all().delete()
            self.stdout.write(self.style.SUCCESS(f'Successfully deleted {count} theme park tasks'))
            
        if task_type == 'r1d3' or task_type == 'all':
            count = R1D3Task.objects.count()
            R1D3Task.objects.all().delete()
            self.stdout.write(self.style.SUCCESS(f'Successfully deleted {count} R1D3 tasks'))
