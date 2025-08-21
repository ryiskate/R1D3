"""
Django management command to seed the database with initial data
Usage: python manage.py seed_database
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from django.conf import settings
import os


class Command(BaseCommand):
    help = 'Seed the database with initial admin users and basic data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--admin-username',
            type=str,
            default='admin',
            help='Username for the admin user (default: admin)'
        )
        parser.add_argument(
            '--admin-email',
            type=str,
            default='admin@r1d3.com',
            help='Email for the admin user (default: admin@r1d3.com)'
        )
        parser.add_argument(
            '--admin-password',
            type=str,
            default=None,
            help='Password for the admin user (will prompt if not provided)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force creation even if users already exist'
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Starting database seeding process...')
        )

        try:
            with transaction.atomic():
                self.create_admin_users(options)
                self.create_initial_data()
                
            self.stdout.write(
                self.style.SUCCESS('Database seeding completed successfully!')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error during seeding: {str(e)}')
            )
            raise

    def create_admin_users(self, options):
        """Create admin users"""
        self.stdout.write('Creating admin users...')
        
        admin_username = options['admin_username']
        admin_email = options['admin_email']
        admin_password = options['admin_password']
        force = options['force']

        # Check if admin user already exists
        if User.objects.filter(username=admin_username).exists():
            if not force:
                self.stdout.write(
                    self.style.WARNING(f'Admin user "{admin_username}" already exists. Use --force to recreate.')
                )
                return
            else:
                # Delete existing user if force is True
                User.objects.filter(username=admin_username).delete()
                self.stdout.write(
                    self.style.WARNING(f'Deleted existing admin user "{admin_username}"')
                )

        # Get password if not provided
        if not admin_password:
            admin_password = os.environ.get('ADMIN_PASSWORD')
            if not admin_password:
                from getpass import getpass
                admin_password = getpass(f'Enter password for admin user "{admin_username}": ')

        # Create superuser
        admin_user = User.objects.create_superuser(
            username=admin_username,
            email=admin_email,
            password=admin_password,
            first_name='System',
            last_name='Administrator'
        )

        self.stdout.write(
            self.style.SUCCESS(f'Created admin user: {admin_username}')
        )

        # Create additional staff users
        staff_users = [
            {
                'username': 'project_manager',
                'email': 'pm@r1d3.com',
                'first_name': 'Project',
                'last_name': 'Manager',
                'is_staff': True,
                'is_superuser': False
            },
            {
                'username': 'developer',
                'email': 'dev@r1d3.com',
                'first_name': 'Lead',
                'last_name': 'Developer',
                'is_staff': True,
                'is_superuser': False
            },
            {
                'username': 'content_manager',
                'email': 'content@r1d3.com',
                'first_name': 'Content',
                'last_name': 'Manager',
                'is_staff': True,
                'is_superuser': False
            }
        ]

        for user_data in staff_users:
            username = user_data['username']
            
            if User.objects.filter(username=username).exists():
                if not force:
                    self.stdout.write(
                        self.style.WARNING(f'User "{username}" already exists. Skipping.')
                    )
                    continue
                else:
                    User.objects.filter(username=username).delete()

            # Use default password for staff users
            default_password = 'R1D3_2025!'
            
            user = User.objects.create_user(
                username=user_data['username'],
                email=user_data['email'],
                password=default_password,
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                is_staff=user_data['is_staff'],
                is_superuser=user_data['is_superuser']
            )

            self.stdout.write(
                self.style.SUCCESS(f'Created staff user: {username} (password: {default_password})')
            )

    def create_initial_data(self):
        """Create initial application data"""
        self.stdout.write('Creating initial application data...')
        
        # Import models here to avoid circular imports
        from projects.models import Team
        from strategy.models import StrategyMilestone
        
        # Create default teams
        teams_data = [
            {
                'name': 'Development Team',
                'description': 'Core development team for R1D3 projects'
            },
            {
                'name': 'Content Team',
                'description': 'Content creation and management team'
            },
            {
                'name': 'Marketing Team',
                'description': 'Marketing and social media team'
            }
        ]

        for team_data in teams_data:
            team, created = Team.objects.get_or_create(
                name=team_data['name'],
                defaults={'description': team_data['description']}
            )
            if created:
                self.stdout.write(f'Created team: {team.name}')
            else:
                self.stdout.write(f'Team already exists: {team.name}')

        # Create initial strategy milestones
        milestones_data = [
            {
                'title': 'Release First Indie Game',
                'description': 'Complete development and release our first indie game',
                'status': 'in_progress',
                'priority': 'high'
            },
            {
                'title': 'Build Community Platform',
                'description': 'Develop and launch community engagement platform',
                'status': 'planning',
                'priority': 'medium'
            },
            {
                'title': 'Establish Brand Identity',
                'description': 'Create consistent brand identity across all platforms',
                'status': 'planning',
                'priority': 'medium'
            }
        ]

        for milestone_data in milestones_data:
            milestone, created = StrategyMilestone.objects.get_or_create(
                title=milestone_data['title'],
                defaults={
                    'description': milestone_data['description'],
                    'status': milestone_data['status'],
                    'priority': milestone_data['priority']
                }
            )
            if created:
                self.stdout.write(f'Created milestone: {milestone.title}')
            else:
                self.stdout.write(f'Milestone already exists: {milestone.title}')

        self.stdout.write(
            self.style.SUCCESS('Initial data creation completed!')
        )
