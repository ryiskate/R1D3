from django.core.management.base import BaseCommand
from projects.game_models import GameMilestone, GameTask
from core.context_processors import get_phase_for_milestone
import textwrap
import os
import time
from datetime import datetime

class Command(BaseCommand):
    help = 'Display the current milestone status in the console with real-time updates'

    def add_arguments(self, parser):
        parser.add_argument('--refresh', type=int, default=5, help='Refresh interval in seconds')
        parser.add_argument('--no-monitor', action='store_true', help='Show once and exit (no monitoring)')

    def clear_screen(self):
        """Clear the console screen"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def get_current_milestone_info(self):
        """Get information about the current milestone"""
        # Find milestones with in_progress status
        in_progress_milestones = GameMilestone.objects.filter(status='in_progress')
        
        if in_progress_milestones.exists():
            # Get the first in-progress milestone
            milestone = in_progress_milestones.first()
            return {
                'source': 'direct',
                'milestone': milestone,
                'title': milestone.title,
                'game': milestone.game.title,
                'status': milestone.status,
                'phase_info': get_phase_for_milestone(milestone.title)
            }
        
        # If no in-progress milestones found, fall back to task-based detection
        in_progress_tasks = GameTask.objects.filter(status='in_progress')
        
        if in_progress_tasks.exists():
            # Get the first in-progress task
            task = in_progress_tasks.first()
            
            if task and task.milestone:
                # Get milestone info from the in-progress task
                milestone = task.milestone
                return {
                    'source': 'task',
                    'milestone': milestone,
                    'title': milestone.title,
                    'game': milestone.game.title,
                    'status': milestone.status,
                    'phase_info': get_phase_for_milestone(milestone.title)
                }
            elif task:
                # Task has no milestone, use task info
                return {
                    'source': 'task_no_milestone',
                    'task': task,
                    'title': task.title,
                    'game': task.game.title if task.game else 'No Game',
                    'company_section': task.company_section
                }
        
        # Default fallback if no milestone or task is found
        return {
            'source': 'default',
            'title': 'No Active Milestone',
            'phase_name': 'Unknown Phase',
            'phase_type': 'unknown'
        }

    def display_milestone_banner(self, info):
        """Display a prominent banner with milestone information"""
        self.clear_screen()
        
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Create a colorful banner
        self.stdout.write("\n")
        self.stdout.write(self.style.SUCCESS("╔" + "═" * 78 + "╗"))
        self.stdout.write(self.style.SUCCESS("║" + " " * 78 + "║"))
        self.stdout.write(self.style.SUCCESS("║" + f"  R1D3 MILESTONE STATUS MONITOR - {now}".ljust(77) + "║"))
        self.stdout.write(self.style.SUCCESS("║" + " " * 78 + "║"))
        self.stdout.write(self.style.SUCCESS("╚" + "═" * 78 + "╝"))
        self.stdout.write("\n")
        
        if info['source'] in ['direct', 'task']:
            milestone = info['milestone']
            phase_info = info['phase_info']
            
            # Display phase information
            self.stdout.write(self.style.WARNING("╔" + "═" * 78 + "╗"))
            self.stdout.write(self.style.WARNING("║" + f"  COMPANY PHASE: {phase_info['name']}".ljust(77) + "║"))
            self.stdout.write(self.style.WARNING("║" + f"  PHASE TYPE: {phase_info['phase_type']} (Order: {phase_info['order']})".ljust(77) + "║"))
            self.stdout.write(self.style.WARNING("╚" + "═" * 78 + "╝"))
            self.stdout.write("\n")
            
            # Display milestone information
            self.stdout.write(self.style.ERROR("╔" + "═" * 78 + "╗"))
            self.stdout.write(self.style.ERROR("║" + " " * 78 + "║"))
            self.stdout.write(self.style.ERROR("║" + f"  CURRENT MILESTONE: {milestone.title}".ljust(77) + "║"))
            self.stdout.write(self.style.ERROR("║" + f"  GAME: {milestone.game.title}".ljust(77) + "║"))
            
            # Status with color based on status
            status_display = "IN PROGRESS" if milestone.status == 'in_progress' else "COMPLETED" if milestone.status == 'completed' else "NOT STARTED"
            status_style = self.style.SUCCESS if milestone.status == 'in_progress' else self.style.WARNING
            self.stdout.write(self.style.ERROR("║" + f"  STATUS: {status_style(status_display)}".ljust(77) + "║"))
            
            # Due date with color based on proximity
            due_date = milestone.due_date if milestone.due_date else "Not set"
            self.stdout.write(self.style.ERROR("║" + f"  DUE DATE: {due_date}".ljust(77) + "║"))
            self.stdout.write(self.style.ERROR("║" + " " * 78 + "║"))
            
            # Description (wrapped)
            if milestone.description:
                self.stdout.write(self.style.ERROR("║" + "  DESCRIPTION:".ljust(77) + "║"))
                wrapped_desc = textwrap.wrap(milestone.description, width=74)
                for line in wrapped_desc[:3]:  # Limit to 3 lines
                    self.stdout.write(self.style.ERROR("║" + f"    {line}".ljust(77) + "║"))
                if len(wrapped_desc) > 3:
                    self.stdout.write(self.style.ERROR("║" + "    ...".ljust(77) + "║"))
            
            self.stdout.write(self.style.ERROR("║" + " " * 78 + "║"))
            self.stdout.write(self.style.ERROR("╚" + "═" * 78 + "╝"))
            
            # Related tasks
            tasks = GameTask.objects.filter(milestone=milestone)
            if tasks.exists():
                self.stdout.write("\n")
                self.stdout.write(self.style.SUCCESS("╔" + "═" * 78 + "╗"))
                self.stdout.write(self.style.SUCCESS("║" + f"  RELATED TASKS ({tasks.count()})".ljust(77) + "║"))
                self.stdout.write(self.style.SUCCESS("╚" + "═" * 78 + "╝"))
                
                for i, task in enumerate(tasks[:5], 1):  # Show only first 5 tasks
                    status_color = self.style.SUCCESS if task.status == 'in_progress' else self.style.WARNING
                    self.stdout.write(f"  {i}. {task.title} - Status: {status_color(task.status)}")
                
                if tasks.count() > 5:
                    self.stdout.write(f"  ... and {tasks.count() - 5} more tasks not shown")
        
        elif info['source'] == 'task_no_milestone':
            task = info['task']
            self.stdout.write(self.style.WARNING("╔" + "═" * 78 + "╗"))
            self.stdout.write(self.style.WARNING("║" + "  WARNING: IN-PROGRESS TASK HAS NO MILESTONE".ljust(77) + "║"))
            self.stdout.write(self.style.WARNING("╚" + "═" * 78 + "╝"))
            self.stdout.write("\n")
            self.stdout.write(f"  Task: {task.title}")
            self.stdout.write(f"  Company Section: {task.company_section}")
        
        else:  # Default
            self.stdout.write(self.style.WARNING("╔" + "═" * 78 + "╗"))
            self.stdout.write(self.style.WARNING("║" + "  NO ACTIVE MILESTONE FOUND".ljust(77) + "║"))
            self.stdout.write(self.style.WARNING("╚" + "═" * 78 + "╝"))
            self.stdout.write("\n")
            self.stdout.write("  No milestone is currently marked as in-progress.")
            self.stdout.write("  Use 'python manage.py set_milestone_status --milestone \"Title\" --status in_progress'")
            self.stdout.write("  to set a milestone as the current active milestone.")

    def handle(self, *args, **options):
        refresh_interval = options['refresh']
        no_monitor = options['no_monitor']
        
        try:
            if no_monitor:
                # Show once and exit
                info = self.get_current_milestone_info()
                self.display_milestone_banner(info)
            else:
                # Monitor mode with refresh
                self.stdout.write(self.style.SUCCESS("Starting milestone monitor..."))
                self.stdout.write(self.style.SUCCESS(f"Refresh interval: {refresh_interval} seconds"))
                self.stdout.write(self.style.SUCCESS("Press Ctrl+C to exit"))
                
                try:
                    while True:
                        info = self.get_current_milestone_info()
                        self.display_milestone_banner(info)
                        self.stdout.write("\n")
                        self.stdout.write(f"Monitor refreshing every {refresh_interval} seconds. Press Ctrl+C to exit.")
                        time.sleep(refresh_interval)
                except KeyboardInterrupt:
                    self.stdout.write(self.style.SUCCESS("\nMilestone monitor stopped."))
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {str(e)}"))
