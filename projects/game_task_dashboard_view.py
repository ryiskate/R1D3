from django.shortcuts import render, get_object_or_404
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q, Sum, Case, When, IntegerField
from django.utils import timezone
from django.urls import reverse
from datetime import timedelta

from core.mixins import BreadcrumbMixin

from .game_models import GameProject, GameMilestone, GDDFeature
from .task_models import GameDevelopmentTask

class GameTaskDashboardView(BreadcrumbMixin, LoginRequiredMixin, View):
    """
    Comprehensive task management dashboard for game tasks
    """
    template_name = 'projects/game_task_dashboard.html'
    
    def get_breadcrumbs(self):
        breadcrumbs = [
            {'title': 'Game Development', 'url': reverse('games:dashboard')},
            {'title': 'Tasks', 'url': None}
        ]
        
        # Add game to breadcrumbs if available
        game_id = self.kwargs.get('game_id') or self.request.GET.get('game')
        if game_id:
            try:
                game = GameProject.objects.get(pk=game_id)
                # Update breadcrumbs with game info
                breadcrumbs = [
                    {'title': 'Game Development', 'url': reverse('games:dashboard')},
                    {'title': game.title, 'url': reverse('games:game_detail', args=[game.id])},
                    {'title': 'Tasks', 'url': None}
                ]
            except GameProject.DoesNotExist:
                pass
        
        return breadcrumbs
    
    def get(self, request, game_id=None):
        context = {}
        
        # Get game if specified in URL or query parameter
        if game_id:
            # Game ID from URL parameter
            game = get_object_or_404(GameProject, pk=game_id)
            context['game'] = game
            tasks = GameDevelopmentTask.objects.filter(game=game)
        elif request.GET.get('game'):
            # Game ID from query parameter
            game_id = request.GET.get('game')
            game = get_object_or_404(GameProject, pk=game_id)
            context['game'] = game
            tasks = GameDevelopmentTask.objects.filter(game=game)
        else:
            # If no game specified, show all tasks the user has access to
            if request.user.is_staff:
                tasks = GameDevelopmentTask.objects.all()
            else:
                # Get tasks from games where user is a team member or lead
                tasks = GameDevelopmentTask.objects.filter(
                    Q(game__team_members=request.user) | 
                    Q(game__lead_developer=request.user) | 
                    Q(game__lead_designer=request.user) |
                    Q(game__lead_artist=request.user) |
                    Q(assigned_to=request.user)
                ).distinct()
        
        # Filter by assigned user if requested
        if request.GET.get('my_tasks'):
            tasks = tasks.filter(assigned_to=request.user)
        
        # Filter by status if provided
        status = request.GET.get('status')
        if status:
            tasks = tasks.filter(status=status)
        
        # Filter by task type if provided
        task_type = request.GET.get('type')
        if task_type:
            tasks = tasks.filter(task_type=task_type)
        
        # Filter by milestone if provided
        milestone_id = request.GET.get('milestone')
        if milestone_id:
            tasks = tasks.filter(milestone_id=milestone_id)
        
        # Filter by priority if provided
        priority = request.GET.get('priority')
        if priority:
            tasks = tasks.filter(priority=priority)
            
        # Filter by company section if provided
        company_section = request.GET.get('company_section')
        if company_section:
            tasks = tasks.filter(company_section=company_section)
        
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
                tasks = tasks.filter(due_date__lt=today, status__in=['backlog', 'to_do', 'in_progress', 'in_review'])
            elif due_date_filter == 'no_date':
                tasks = tasks.filter(due_date__isnull=True)
        
        # Default ordering
        tasks = tasks.order_by('-priority', 'due_date')
        
        # Get task statistics
        context['task_stats'] = {
            'total': tasks.count(),
            'completed': tasks.filter(status='done').count(),
            'done': tasks.filter(status='done').count(),  # Adding 'done' key for consistency
            'in_progress': tasks.filter(status='in_progress').count(),
            'to_do': tasks.filter(status='to_do').count(),
            'backlog': tasks.filter(status='backlog').count(),
            'in_review': tasks.filter(status='in_review').count(),
            'blocked': tasks.filter(status='blocked').count(),
            'completion_rate': round(tasks.filter(status='done').count() / max(tasks.count(), 1) * 100),
            'estimated_hours': tasks.aggregate(Sum('estimated_hours'))['estimated_hours__sum'] or 0,
            'actual_hours': tasks.aggregate(Sum('actual_hours'))['actual_hours__sum'] or 0,
        }
        
        # Get task counts by type
        task_types = tasks.values('task_type').annotate(count=Count('id')).order_by('-count')
        context['task_types'] = task_types
        
        # Get task counts by priority
        priority_counts = tasks.values('priority').annotate(count=Count('id')).order_by('priority')
        context['priority_counts'] = priority_counts
        
        # Get recent tasks
        context['recent_tasks'] = tasks.order_by('-updated_at')[:10]
        
        # Get upcoming due tasks
        today = timezone.now().date()
        context['upcoming_tasks'] = tasks.filter(
            due_date__gte=today,
            status__in=['backlog', 'to_do', 'in_progress', 'in_review']
        ).order_by('due_date')[:10]
        
        # Get overdue tasks
        context['overdue_tasks'] = tasks.filter(
            due_date__lt=today,
            status__in=['backlog', 'to_do', 'in_progress', 'in_review']
        ).order_by('due_date')
        
        # Get milestones if a game is specified
        if game_id:
            context['milestones'] = GameMilestone.objects.filter(game_id=game_id).order_by('due_date')
            
            # Calculate milestone progress
            for milestone in context['milestones']:
                milestone_tasks = tasks.filter(milestone=milestone)
                total = milestone_tasks.count()
                completed = milestone_tasks.filter(status='done').count()
                milestone.progress = round(completed / max(total, 1) * 100)
                milestone.total_tasks = total
                milestone.completed_tasks = completed
        
        # Add task status counts for filters
        context['status_counts'] = {
            status[0]: tasks.filter(status=status[0]).count() 
            for status in GameDevelopmentTask.STATUS_CHOICES
        }
        
        # Add task type counts for filters
        task_types = set(tasks.values_list('task_type', flat=True).distinct())
        context['type_counts'] = {
            task_type: tasks.filter(task_type=task_type).count() 
            for task_type in task_types if task_type
        }
        
        # Add priority counts for filters
        context['priority_counts'] = {
            priority[0]: tasks.filter(priority=priority[0]).count() 
            for priority in GameDevelopmentTask.PRIORITY_CHOICES
        }
        
        # Add tasks to context
        context['tasks'] = tasks
        
        # Add today's date for template comparison
        context['today'] = timezone.now().date()
        
        # Add batch update URL to context
        context['batch_update_url'] = 'games:game_task_batch_update'
        
        # Add all games to context for the game projects filter section
        if request.user.is_staff:
            context['games'] = GameProject.objects.all()
        else:
            # Only show games where user is a team member or lead
            context['games'] = GameProject.objects.filter(
                Q(team_members=request.user) | 
                Q(lead_developer=request.user) | 
                Q(lead_designer=request.user) |
                Q(lead_artist=request.user)
            ).distinct()
        
        return render(request, self.template_name, context)
