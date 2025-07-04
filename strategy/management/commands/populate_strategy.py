from django.core.management.base import BaseCommand
from django.utils import timezone
from strategy.models import StrategyPhase, StrategyMilestone

class Command(BaseCommand):
    help = 'Populates the database with initial company strategy phases and milestones'

    def handle(self, *args, **options):
        # Clear existing data
        self.stdout.write('Clearing existing strategy data...')
        StrategyMilestone.objects.all().delete()
        StrategyPhase.objects.all().delete()
        
        # Create phases
        self.stdout.write('Creating strategy phases...')
        
        # Phase 1: Indie Game Development
        phase1 = StrategyPhase.objects.create(
            name="Indie Game Development",
            phase_type="indie_dev",
            description="Building a foundation in game development through education and indie projects. "
                       "Focus on learning game development tools, creating indie games, and establishing "
                       "industry connections.",
            order=1,
            start_year=2025,
            end_year=2028,
            is_current=True,
            is_completed=False
        )
        
        # Phase 2: Arcade Machines
        phase2 = StrategyPhase.objects.create(
            name="Arcade Machine Development",
            phase_type="arcade",
            description="Expanding into physical gaming experiences through arcade machine development. "
                       "Learn hardware integration, develop custom controllers, create arcade-specific "
                       "game experiences, and establish arcade locations.",
            order=2,
            start_year=2028,
            end_year=2032,
            is_current=False,
            is_completed=False
        )
        
        # Phase 3: Theme Park Attractions
        phase3 = StrategyPhase.objects.create(
            name="Theme Park Attractions",
            phase_type="theme_park",
            description="Creating immersive physical experiences through theme park attractions. "
                       "Develop 3D attractions and simulators, design and build roller coasters, "
                       "create themed environments, and establish full theme park experiences.",
            order=3,
            start_year=2032,
            end_year=2038,
            is_current=False,
            is_completed=False
        )
        
        # Create milestones for Phase 1
        self.stdout.write('Creating milestones for Phase 1...')
        milestones_phase1 = [
            {
                "title": "Complete Game Development Course",
                "description": "Finish comprehensive game development course covering Unity, Unreal Engine, and game design principles.",
                "order": 1,
                "target_date": timezone.now().date().replace(year=2025, month=6, day=30),
                "is_completed": True,
                "completion_date": timezone.now().date().replace(year=2025, month=6, day=15)
            },
            {
                "title": "Release First Indie Game",
                "description": "Develop and release our first indie game on Steam and mobile platforms.",
                "order": 2,
                "target_date": timezone.now().date().replace(year=2026, month=3, day=15),
                "is_completed": False
            },
            {
                "title": "Establish Game Development Blog",
                "description": "Create and grow a game development blog with tutorials and industry insights.",
                "order": 3,
                "target_date": timezone.now().date().replace(year=2026, month=9, day=1),
                "is_completed": False
            },
            {
                "title": "Launch Game Development Education Platform",
                "description": "Create an online platform for teaching game development skills to others.",
                "order": 4,
                "target_date": timezone.now().date().replace(year=2027, month=6, day=30),
                "is_completed": False
            },
            {
                "title": "Attend Major Game Industry Conference",
                "description": "Participate in a major game industry conference to network and showcase our games.",
                "order": 5,
                "target_date": timezone.now().date().replace(year=2027, month=11, day=15),
                "is_completed": False
            }
        ]
        
        for milestone_data in milestones_phase1:
            StrategyMilestone.objects.create(phase=phase1, **milestone_data)
        
        # Create milestones for Phase 2
        self.stdout.write('Creating milestones for Phase 2...')
        milestones_phase2 = [
            {
                "title": "Hardware Integration Research",
                "description": "Complete research on hardware integration for arcade machines including controls, sensors, and displays.",
                "order": 1,
                "target_date": timezone.now().date().replace(year=2028, month=6, day=30),
                "is_completed": False
            },
            {
                "title": "Prototype First Arcade Cabinet",
                "description": "Build a prototype arcade cabinet with custom controls and game integration.",
                "order": 2,
                "target_date": timezone.now().date().replace(year=2029, month=3, day=15),
                "is_completed": False
            },
            {
                "title": "Develop Arcade-Specific Game",
                "description": "Create a game specifically designed for arcade machine play with unique controls.",
                "order": 3,
                "target_date": timezone.now().date().replace(year=2029, month=12, day=1),
                "is_completed": False
            },
            {
                "title": "Open First Arcade Location",
                "description": "Establish our first physical arcade location featuring our custom machines.",
                "order": 4,
                "target_date": timezone.now().date().replace(year=2031, month=6, day=30),
                "is_completed": False
            }
        ]
        
        for milestone_data in milestones_phase2:
            StrategyMilestone.objects.create(phase=phase2, **milestone_data)
        
        # Create milestones for Phase 3
        self.stdout.write('Creating milestones for Phase 3...')
        milestones_phase3 = [
            {
                "title": "3D Attraction Prototype",
                "description": "Develop a prototype for an immersive 3D attraction combining VR and physical elements.",
                "order": 1,
                "target_date": timezone.now().date().replace(year=2032, month=9, day=30),
                "is_completed": False
            },
            {
                "title": "Simulator Technology Development",
                "description": "Research and develop motion simulator technology for theme park rides.",
                "order": 2,
                "target_date": timezone.now().date().replace(year=2033, month=8, day=15),
                "is_completed": False
            },
            {
                "title": "First Roller Coaster Design",
                "description": "Complete the design for our first game-themed roller coaster attraction.",
                "order": 3,
                "target_date": timezone.now().date().replace(year=2034, month=7, day=1),
                "is_completed": False
            },
            {
                "title": "Themed Environment Prototype",
                "description": "Create a prototype of a fully themed environment based on our game properties.",
                "order": 4,
                "target_date": timezone.now().date().replace(year=2035, month=6, day=30),
                "is_completed": False
            },
            {
                "title": "Theme Park Land Opening",
                "description": "Open our first themed land within an existing theme park.",
                "order": 5,
                "target_date": timezone.now().date().replace(year=2037, month=5, day=15),
                "is_completed": False
            }
        ]
        
        for milestone_data in milestones_phase3:
            StrategyMilestone.objects.create(phase=phase3, **milestone_data)
        
        self.stdout.write(self.style.SUCCESS('Successfully populated company strategy data!'))
