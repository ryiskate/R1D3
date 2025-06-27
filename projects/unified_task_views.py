from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Q, Sum
from django.utils import timezone
from datetime import timedelta

from .task_models import (
    BaseTask, GameDevelopmentTask, EducationTask, SocialMediaTask, 
    ArcadeTask, ThemeParkTask, R1D3Task
)
from .game_models import GameProject, GameMilestone

class UnifiedTaskDashboardView(LoginRequiredMixin, View):
    """
    A unified dashboard view that can work with any task model type
    """
    template_name = 'projects/unified_task_dashboard.html'
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.task_model = None
        self.section_name = None
        self.section_filter = None
        self.section_model = None
        self.section_field = None
    
    def get(self, request, *args, **kwargs):
        context = {}
        
        # Get the task model based on the section
        if not self.task_model:
            raise ValueError("Task model must be set in the subclass")
            
        # Add section name to context
        context['section_name'] = self.section_name or "Tasks"
        
        # Get section-specific object if specified
        section_object_id = request.GET.get(self.section_field) if self.section_field else None
        if section_object_id and self.section_model:
            section_object = get_object_or_404(self.section_model, pk=section_object_id)
            context['section_object'] = section_object
            filter_kwargs = {self.section_field: section_object}
            tasks = self.task_model.objects.filter(**filter_kwargs)
        else:
            # If no section object specified, show all tasks the user has access to
            if request.user.is_staff:
                tasks = self.task_model.objects.all()
            else:
                # Get tasks assigned to the user or where user has special access
                tasks = self.task_model.objects.filter(
                    Q(assigned_to=request.user) | self.get_section_specific_access(request.user)
                ).distinct()
        
        # Apply common filters
        tasks = self.apply_common_filters(request, tasks)
        
        # Get task statistics
        context['task_stats'] = self.get_task_stats(tasks)
        
        # Get task counts by status, priority, etc.
        context.update(self.get_filter_counts(tasks))
        
        # Get recent, upcoming, and overdue tasks
        context.update(self.get_time_based_tasks(tasks))
        
        # Add section-specific context
        context.update(self.get_section_specific_context(request, tasks))
        
        # Add tasks to context
        context['tasks'] = tasks
        
        # Add today's date for template comparison
        context['today'] = timezone.now().date()
        
        return render(request, self.template_name, context)
    
    def get_section_specific_access(self, user):
        """
        Get section-specific access Q object for filtering tasks
        Override in subclasses to add section-specific access rules
        """
        return Q()
    
    def apply_common_filters(self, request, tasks):
        """Apply common filters to tasks based on request parameters"""
        # Filter by assigned user if requested
        assigned_to = request.GET.get('assigned_to')
        if assigned_to:
            if assigned_to == 'me':
                tasks = tasks.filter(assigned_to=request.user)
            else:
                tasks = tasks.filter(assigned_to_id=assigned_to)
        
        # Filter by status if provided
        status = request.GET.get('status')
        if status:
            tasks = tasks.filter(status=status)
        
        # Filter by task type if provided
        task_type = request.GET.get('task_type')
        if task_type:
            tasks = tasks.filter(task_type=task_type)
        
        # Filter by priority if provided
        priority = request.GET.get('priority')
        if priority:
            tasks = tasks.filter(priority=priority)
        
        # Filter by due date range
        due_date_filter = request.GET.get('due_date')
        if due_date_filter:
            today = timezone.now().date()
            if due_date_filter == 'today':
                tasks = tasks.filter(due_date=today)
            elif due_date_filter == 'this_week':
                end_of_week = today + timedelta(days=(6 - today.weekday()))
                tasks = tasks.filter(due_date__range=[today, end_of_week])
            elif due_date_filter == 'overdue':
                tasks = tasks.filter(due_date__lt=today, status__in=['backlog', 'to_do', 'todo', 'in_progress', 'in_review'])
            elif due_date_filter == 'no_date':
                tasks = tasks.filter(due_date__isnull=True)
        
        # Default ordering
        tasks = tasks.order_by('-priority', 'due_date')
        
        return tasks
    
    def get_task_stats(self, tasks):
        """Get task statistics for the dashboard"""
        return {
            'total': tasks.count(),
            'completed': tasks.filter(status='done').count(),
            'done': tasks.filter(status='done').count(),
            'in_progress': tasks.filter(status='in_progress').count(),
            'to_do': tasks.filter(status='to_do').count(),
            'backlog': tasks.filter(status='backlog').count(),
            'in_review': tasks.filter(status='in_review').count(),
            'blocked': tasks.filter(status='blocked').count(),
            'completion_rate': round(tasks.filter(status='done').count() / max(tasks.count(), 1) * 100),
            'estimated_hours': tasks.aggregate(Sum('estimated_hours'))['estimated_hours__sum'] or 0,
            'actual_hours': tasks.aggregate(Sum('actual_hours'))['actual_hours__sum'] or 0,
        }
    
    def get_filter_counts(self, tasks):
        """Get counts for various filters"""
        result = {}
        
        # Add task status counts for filters
        result['status_counts'] = {
            status[0]: tasks.filter(status=status[0]).count() 
            for status in self.task_model.STATUS_CHOICES
        }
        
        # Add task type counts for filters
        task_types = set(tasks.values_list('task_type', flat=True).distinct())
        result['type_counts'] = {
            task_type: tasks.filter(task_type=task_type).count() 
            for task_type in task_types if task_type
        }
        
        # Add priority counts for filters
        result['priority_counts'] = {
            priority[0]: tasks.filter(priority=priority[0]).count() 
            for priority in self.task_model.PRIORITY_CHOICES
        }
        
        return result
    
    def get_time_based_tasks(self, tasks):
        """Get recent, upcoming, and overdue tasks"""
        result = {}
        
        # Get recent tasks
        result['recent_tasks'] = tasks.order_by('-updated_at')[:10]
        
        # Get upcoming due tasks
        today = timezone.now().date()
        result['upcoming_tasks'] = tasks.filter(
            due_date__gte=today,
            status__in=['backlog', 'to_do', 'in_progress', 'in_review']
        ).order_by('due_date')[:10]
        
        # Get overdue tasks
        result['overdue_tasks'] = tasks.filter(
            due_date__lt=today,
            status__in=['backlog', 'to_do', 'in_progress', 'in_review']
        ).order_by('due_date')
        
        return result
    
    def get_section_specific_context(self, request, tasks):
        """Get section-specific context data"""
        # Override in subclasses to add section-specific context
        return {}


# Specialized dashboard views for each task type
class GameTaskDashboardView(UnifiedTaskDashboardView):
    """Game development task dashboard"""
    template_name = 'projects/game_task_dashboard.html'
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.task_model = GameDevelopmentTask
        self.section_name = "Game Development Tasks"
        self.section_model = GameProject
        self.section_field = "game"
    
    def get_section_specific_access(self, user):
        """Game-specific access rules"""
        return (
            Q(game__team_members=user) | 
            Q(game__lead_developer=user) | 
            Q(game__lead_designer=user) |
            Q(game__lead_artist=user)
        )
    
    def get_section_specific_context(self, request, tasks):
        """Game-specific context data"""
        context = {}
        
        # Get game if specified
        game_id = request.GET.get('game')
        if game_id:
            # Get milestones for the game
            context['milestones'] = GameMilestone.objects.filter(game_id=game_id).order_by('due_date')
            
            # Calculate milestone progress
            for milestone in context['milestones']:
                milestone_tasks = tasks.filter(milestone=milestone)
                total = milestone_tasks.count()
                completed = milestone_tasks.filter(status='done').count()
                milestone.progress = round(completed / max(total, 1) * 100)
                milestone.total_tasks = total
                milestone.completed_tasks = completed
        
        return context


class EducationTaskDashboardView(View):  # Temporarily removed LoginRequiredMixin for debugging
    """Education task dashboard"""
    template_name = 'education/test_tasks.html'
    
    def get(self, request, *args, **kwargs):
        print("DEBUG: EducationTaskDashboardView is being called")
        
        # Get all education tasks directly
        tasks = EducationTask.objects.all()
        print(f"DEBUG: Total education tasks in database: {tasks.count()}")
        
        # Create simple context with tasks
        context = {
            'tasks': tasks,
            'task_stats': {
                'to_do': tasks.filter(status='to_do').count(),
                'in_progress': tasks.filter(status='in_progress').count(),
                'in_review': tasks.filter(status='in_review').count(),
                'done': tasks.filter(status='done').count(),
                'backlog': tasks.filter(status='backlog').count(),
            },
            'section_name': 'Education Tasks'
        }
        
        # Print debug info
        for task in tasks[:3]:
            print(f"DEBUG: Task {task.id}: {task.title} (Status: {task.status})")
        print(f"DEBUG: Context task count: {len(context['tasks'])}")
        print(f"DEBUG: Context stats: {context['task_stats']}")
        
        return render(request, self.template_name, context)


class SocialMediaTaskDashboardView(UnifiedTaskDashboardView):
    """Social media task dashboard"""
    template_name = 'projects/social_media_task_dashboard.html'
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.task_model = SocialMediaTask
        self.section_name = "Social Media Tasks"


class ArcadeTaskDashboardView(UnifiedTaskDashboardView):
    """Arcade task dashboard"""
    template_name = 'projects/arcade_task_dashboard.html'
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.task_model = ArcadeTask
        self.section_name = "Arcade Tasks"


class ThemeParkTaskDashboardView(UnifiedTaskDashboardView):
    """Theme park task dashboard"""
    template_name = 'projects/theme_park_task_dashboard.html'
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.task_model = ThemeParkTask
        self.section_name = "Theme Park Tasks"


class R1D3TaskDashboardView(UnifiedTaskDashboardView):
    """General R1D3 task dashboard"""
    template_name = 'projects/r1d3_task_dashboard.html'
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.task_model = R1D3Task
        self.section_name = "R1D3 Tasks"
