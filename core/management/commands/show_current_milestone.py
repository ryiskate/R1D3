from django.core.management.base import BaseCommand
from projects.game_models import GameMilestone, GameTask
from core.context_processors import get_phase_for_milestone
import textwrap
import os

class Command(BaseCommand):
    help = 'Show the current in-progress milestone and related information'

    def add_arguments(self, parser):
        parser.add_argument('--verbose', action='store_true', help='Show detailed information')

    def handle(self, *args, **options):
        verbose = options.get('verbose', False)
        
        # Clear screen for better visibility
        os.system('cls' if os.name == 'nt' else 'clear')
        
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS("               R1D3 CURRENT MILESTONE STATUS"))
        self.stdout.write("=" * 60 + "\n")
        
        try:
            # Find milestones with in_progress status
            in_progress_milestones = GameMilestone.objects.filter(status='in_progress')
            
            if in_progress_milestones.exists():
                count = in_progress_milestones.count()
                if count > 1:
                    self.stdout.write(self.style.WARNING(f"[FOUND] {count} in-progress milestones detected"))
                    self.stdout.write(self.style.WARNING("Note: Only one milestone should be in progress at a time."))
                    
                    # Display a list of all in-progress milestones
                    self.stdout.write("\nAll in-progress milestones:")
                    for i, m in enumerate(in_progress_milestones):
                        self.stdout.write(f"{i+1}. {m.title} - {m.game.title}")
                    self.stdout.write("\nShowing details for the first in-progress milestone:\n")
                else:
                    self.stdout.write(self.style.SUCCESS("[FOUND] In-progress milestone detected directly"))
                
                # Get the first in-progress milestone
                milestone = in_progress_milestones.first()
                self.display_milestone_info(milestone, verbose)
            else:
                self.stdout.write(self.style.WARNING("[NOT FOUND] No non-completed milestones found"))
                
                # Find tasks with 'in_progress' status
                in_progress_tasks = GameTask.objects.filter(status='in_progress')
                
                if in_progress_tasks.exists():
                    self.stdout.write(self.style.SUCCESS("[FOUND] In-progress tasks detected"))
                    
                    # Get the first in-progress task
                    task = in_progress_tasks.first()
                    self.stdout.write(f"  Task: {task.title}")
                    
                    if task.milestone:
                        self.stdout.write(self.style.SUCCESS("[FOUND] Task has associated milestone"))
                        self.display_milestone_info(task.milestone, verbose)
                    else:
                        self.stdout.write(self.style.ERROR("[NOT FOUND] In-progress task has no milestone"))
                        self.stdout.write(f"  Task company section: {task.company_section}")
                else:
                    self.stdout.write(self.style.ERROR("[NOT FOUND] No in-progress tasks found"))
                    self.stdout.write(self.style.WARNING("Using default milestone: 'Release First Indie Game'"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"[ERROR] {str(e)}"))
            self.stdout.write(self.style.ERROR("Could not determine current milestone status"))
    
    def display_milestone_info(self, milestone, verbose):
        """Display milestone information in a formatted way"""
        # Get phase info
        phase_info = get_phase_for_milestone(milestone.title)
        
        # Format milestone info
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS(f"CURRENT MILESTONE: {milestone.title}"))
        self.stdout.write("=" * 60)
        
        # Basic milestone info table
        self.stdout.write("+" + "-" * 17 + "+" + "-" * 42 + "+")
        self.stdout.write(f"| Game            | {milestone.game.title:<40} |")
        self.stdout.write("+" + "-" * 17 + "+" + "-" * 42 + "+")
        self.stdout.write(f"| Company Phase   | {phase_info['name']:<40} |")
        self.stdout.write("+" + "-" * 17 + "+" + "-" * 42 + "+")
        self.stdout.write(f"| Phase Type      | {phase_info['phase_type']:<40} |")
        self.stdout.write("+" + "-" * 17 + "+" + "-" * 42 + "+")
        self.stdout.write(f"| Phase Order     | {phase_info['order']:<40} |")
        self.stdout.write("+" + "-" * 17 + "+" + "-" * 42 + "+")
        self.stdout.write(f"| Due Date        | {milestone.due_date if milestone.due_date else 'Not set':<40} |")
        self.stdout.write("+" + "-" * 17 + "+" + "-" * 42 + "+")
        
        # Display status based on is_completed field
        status_display = "In Progress" if not milestone.is_completed else "Completed"
        status_style = self.style.SUCCESS if not milestone.is_completed else self.style.WARNING
        self.stdout.write(f"| Status          | {status_style(status_display):<40} |")
        self.stdout.write("+" + "-" * 17 + "+" + "-" * 42 + "+")
        
        if verbose:
            # Description section
            self.stdout.write("\n" + self.style.SUCCESS("MILESTONE DESCRIPTION"))
            self.stdout.write("-" * 60)
            if milestone.description:
                wrapped_desc = textwrap.fill(milestone.description, width=58)
                for line in wrapped_desc.split('\n'):
                    self.stdout.write(f"  {line}")
            else:
                self.stdout.write("  No description available")
            
            # Get related tasks
            tasks = GameTask.objects.filter(milestone=milestone)
            
            # Tasks section
            self.stdout.write("\n" + self.style.SUCCESS(f"RELATED TASKS ({tasks.count()})"))
            self.stdout.write("-" * 60)
            
            if tasks.exists():
                # Table header
                self.stdout.write("+---+-------------------------------------+------------+------------+")
                self.stdout.write("| # | Task Title                          | Status      | Priority    |")
                self.stdout.write("+---+-------------------------------------+------------+------------+")
                
                for i, task in enumerate(tasks[:5], 1):  # Show only first 5 tasks
                    status_style = self.style.SUCCESS if task.status == 'in_progress' else self.style.WARNING
                    title = task.title[:35] + '...' if len(task.title) > 35 else task.title.ljust(35)
                    self.stdout.write(f"| {i:<1} | {title} | {status_style(task.status.ljust(10))} | {task.priority.ljust(10)} |")
                
                self.stdout.write("+---+-------------------------------------+------------+------------+")
                
                if tasks.count() > 5:
                    self.stdout.write(f"  ... and {tasks.count() - 5} more tasks not shown")
            else:
                self.stdout.write("  No tasks associated with this milestone")
        
        self.stdout.write("\n" + "=" * 60)
