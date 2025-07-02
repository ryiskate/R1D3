from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from projects.models import Team

User = get_user_model()

class Command(BaseCommand):
    help = 'Creates initial teams for the R1D3 platform'

    def handle(self, *args, **options):
        # Define initial teams with their names and descriptions
        initial_teams = [
            {
                'name': 'Game Development',
                'description': 'Team responsible for game design, development, and testing'
            },
            {
                'name': 'Education',
                'description': 'Team responsible for educational content and courses'
            },
            {
                'name': 'Social Media',
                'description': 'Team responsible for social media management and marketing'
            },
            {
                'name': 'Arcade',
                'description': 'Team responsible for arcade machine maintenance and operations'
            },
            {
                'name': 'Theme Park',
                'description': 'Team responsible for theme park attractions and operations'
            },
            {
                'name': 'R1D3 Core',
                'description': 'Core team responsible for general company operations'
            },
        ]

        # Get some users to assign as team leaders
        users = list(User.objects.filter(is_active=True)[:6])
        
        teams_created = 0
        teams_existing = 0

        for i, team_data in enumerate(initial_teams):
            # Check if team already exists
            if not Team.objects.filter(name=team_data['name']).exists():
                # Create the team
                team = Team.objects.create(
                    name=team_data['name'],
                    description=team_data['description'],
                )
                
                # Assign a leader if users are available
                if i < len(users):
                    team.leader = users[i]
                    team.save()
                    
                    # Add the leader as a member
                    team.members.add(users[i])
                
                self.stdout.write(self.style.SUCCESS(f'Created team: {team.name}'))
                teams_created += 1
            else:
                self.stdout.write(self.style.WARNING(f'Team already exists: {team_data["name"]}'))
                teams_existing += 1

        self.stdout.write(self.style.SUCCESS(f'Teams created: {teams_created}'))
        self.stdout.write(self.style.WARNING(f'Teams already existing: {teams_existing}'))
