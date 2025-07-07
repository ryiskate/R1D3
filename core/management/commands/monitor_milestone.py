import os
import time
import django
from django.core.management.base import BaseCommand
from django.utils import timezone
from projects.game_models import GameMilestone, GameTask
from core.context_processors import get_phase_for_milestone

class Command(BaseCommand):
    help = 'Monitor the current milestone and display updates when changes occur'

    def add_arguments(self, parser):
        parser.add_argument(
            '--interval',
            type=int,
            default=2,
            help='Polling interval in seconds (default: 2)'
        )
        parser.add_argument(
            '--once',
            action='store_true',
            help='Run once and exit (no continuous monitoring)'
        )

    def clear_screen(self):
        """Clear the console screen"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def get_current_milestone_info(self):
        """Get information about the current milestone"""
        # First try to find a milestone with in_progress status
        in_progress_milestones = GameMilestone.objects.filter(status='in_progress')
        
        if in_progress_milestones.exists():
            # Get the first in-progress milestone
            milestone = in_progress_milestones.first()
            self.stdout.write(self.style.SUCCESS("[FOUND] In-progress milestone detected directly"))
            
            # Get phase information
            self.stdout.write(f"Finding phase for milestone: {milestone.title}")
            phase_info = get_phase_for_milestone(milestone.title)
            self.stdout.write(f"Milestone '{milestone.title}' mapped to {phase_info['name']} phase")
            
            return {
                'source': 'direct',
                'milestone': milestone,
                'title': milestone.title,
                'game': milestone.game.title if milestone.game else 'Unknown Game',
                'is_completed': milestone.is_completed,
                'status_display': 'In Progress' if not milestone.is_completed else 'Completed',
                'phase_info': phase_info
            }
        
        # If no non-completed milestones found, fall back to task-based detection
        self.stdout.write(self.style.WARNING("[NOT FOUND] No in-progress milestone found, checking tasks..."))
        in_progress_tasks = GameTask.objects.filter(status='in_progress')
        
        if in_progress_tasks.exists():
            # Get the first in-progress task
            task = in_progress_tasks.first()
            
            if task and task.milestone:
                # Get milestone info from the in-progress task
                milestone = task.milestone
                self.stdout.write(self.style.SUCCESS(f"[FOUND] In-progress task with milestone: {task.title}"))
                
                # Get phase information
                self.stdout.write(f"Finding phase for milestone: {milestone.title}")
                phase_info = get_phase_for_milestone(milestone.title)
                self.stdout.write(f"Milestone '{milestone.title}' mapped to {phase_info['name']} phase")
                
                return {
                    'source': 'task',
                    'milestone': milestone,
                    'title': milestone.title,
                    'game': task.game.title if task.game else 'Unknown Game',
                    'is_completed': milestone.is_completed,
                    'status_display': 'In Progress' if not milestone.is_completed else 'Completed',
                    'phase_info': phase_info,
                    'task': task
                }
            elif task:
                # Task has no milestone
                self.stdout.write(self.style.WARNING("[PARTIAL] In-progress task found but has no milestone"))
                return {
                    'source': 'task_no_milestone',
                    'task': task,
                    'company_section': task.company_section
                }
        
        # No milestone or task found
        self.stdout.write(self.style.ERROR("[NOT FOUND] No in-progress milestone or task found"))
        return {
            'source': 'default',
            'title': 'Release First Indie Game',
            'game': 'PeacefulFarm',
            'phase_name': 'Indie Game Development',
            'phase_type': 'indie_dev',
            'phase_order': 1
        }

    def display_milestone_info(self, info):
        """Display milestone information in a formatted way"""
        self.clear_screen()
        
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS(f"R1D3 CURRENT MILESTONE STATUS - {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}"))
        self.stdout.write("=" * 60)
        
        if info['source'] == 'direct' or info['source'] == 'task':
            milestone = info['milestone']
            phase_info = info['phase_info']
            
            self.stdout.write("\n" + self.style.SUCCESS(f"CURRENT MILESTONE: {milestone.title}"))
            self.stdout.write("-" * 60)
            
            # Basic milestone info table
            self.stdout.write("+" + "-" * 20 + "+" + "-" * 37 + "+")
            self.stdout.write(f"| Game                | {info['game']:<35} |")
            self.stdout.write("+" + "-" * 20 + "+" + "-" * 37 + "+")
            self.stdout.write(f"| Company Phase       | {phase_info['name']:<35} |")
            self.stdout.write("+" + "-" * 20 + "+" + "-" * 37 + "+")
            self.stdout.write(f"| Phase Type          | {phase_info['phase_type']:<35} |")
            self.stdout.write("+" + "-" * 20 + "+" + "-" * 37 + "+")
            self.stdout.write(f"| Phase Order         | {phase_info['order']:<35} |")
            self.stdout.write("+" + "-" * 20 + "+" + "-" * 37 + "+")
            self.stdout.write(f"| Due Date            | {milestone.due_date if milestone.due_date else 'Not set':<35} |")
            self.stdout.write("+" + "-" * 20 + "+" + "-" * 37 + "+")
            # Display status based on is_completed field
            status_display = "In Progress" if not milestone.is_completed else "Completed"
            status_style = self.style.SUCCESS if not milestone.is_completed else self.style.WARNING
            self.stdout.write(f"| Status              | {status_style(status_display):<35} |")
            self.stdout.write("+" + "-" * 20 + "+" + "-" * 37 + "+")
            
            # Get related tasks
            tasks = GameTask.objects.filter(milestone=milestone)
            
            # Tasks section
            self.stdout.write("\n" + self.style.SUCCESS(f"RELATED TASKS ({tasks.count()})"))
            self.stdout.write("-" * 60)
            
            if tasks.exists():
                # Table header
                self.stdout.write("+---+-------------------------------------+------------+------------+")
                self.stdout.write("| # | Task Title                          | Status     | Priority   |")
                self.stdout.write("+---+-------------------------------------+------------+------------+")
                
                for i, task in enumerate(tasks[:5], 1):  # Show only first 5 tasks
                    title = task.title[:35] + '...' if len(task.title) > 35 else task.title.ljust(35)
                    status_style = self.style.SUCCESS if task.status == 'in_progress' else self.style.WARNING
                    self.stdout.write(f"| {i:<1} | {title} | {status_style(task.status.ljust(10))} | {task.priority.ljust(10)} |")
                
                self.stdout.write("+---+-------------------------------------+------------+------------+")
                
                if tasks.count() > 5:
                    self.stdout.write(f"  ... and {tasks.count() - 5} more tasks not shown")
            else:
                self.stdout.write("  No tasks associated with this milestone")
        
        elif info['source'] == 'task_no_milestone':
            task = info['task']
            self.stdout.write("\n" + self.style.WARNING("WARNING: In-progress task has no milestone"))
            self.stdout.write("-" * 60)
            self.stdout.write(f"Task: {task.title}")
            self.stdout.write(f"Company Section: {task.company_section}")
        
        else:  # Default
            self.stdout.write("\n" + self.style.WARNING("WARNING: No in-progress milestone or task found"))
            self.stdout.write("-" * 60)
            self.stdout.write(f"Using default milestone: '{info['title']}'")
            self.stdout.write(f"Default phase: {info['phase_name']} (Type: {info['phase_type']})")
        
        self.stdout.write("\n" + "=" * 60)

    def handle(self, *args, **options):
        interval = options['interval']
        once = options['once']
        
        self.stdout.write(self.style.SUCCESS("Starting R1D3 Milestone Monitor..."))
        
        last_milestone_title = None
        
        try:
            while True:
                current_info = self.get_current_milestone_info()
                current_milestone_title = current_info.get('title', None)
                
                # Display if it's the first run or if the milestone has changed
                if last_milestone_title is None or current_milestone_title != last_milestone_title:
                    self.display_milestone_info(current_info)
                    last_milestone_title = current_milestone_title
                
                if once:
                    break
                
                # Show instructions for continuous mode
                self.stdout.write(self.style.SUCCESS("Monitoring for milestone changes... Press Ctrl+C to exit"))
                
                # Check every N seconds
                time.sleep(interval)
        
        except KeyboardInterrupt:
            self.stdout.write(self.style.SUCCESS("\nExiting R1D3 Milestone Monitor..."))
