from django.shortcuts import render
from django.views.generic import TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from datetime import date, timedelta

from projects.game_models import GameTask


class ArcadeDashboardView(LoginRequiredMixin, TemplateView):
    """Dashboard view for the Arcade Entertainment department"""
    template_name = 'arcade/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_department'] = 'arcade'
        return context


class ArcadeProjectsView(LoginRequiredMixin, TemplateView):
    """View for managing arcade projects"""
    template_name = 'arcade/projects.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_department'] = 'arcade'
        return context


class LocationsView(LoginRequiredMixin, TemplateView):
    """View for managing arcade locations"""
    template_name = 'arcade/locations.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_department'] = 'arcade'
        return context


class RevenueView(LoginRequiredMixin, TemplateView):
    """View for arcade revenue tracking"""
    template_name = 'arcade/revenue.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_department'] = 'arcade'
        return context


class ArcadeTasksView(LoginRequiredMixin, ListView):
    """View for arcade department tasks"""
    model = GameTask
    template_name = 'arcade/tasks.html'
    context_object_name = 'arcade_tasks'
    
    def get_queryset(self):
        queryset = GameTask.objects.filter(company_section='arcade')
        
        # Apply filters from request parameters
        status = self.request.GET.getlist('status')
        if status:
            queryset = queryset.filter(status__in=status)
            
        priority = self.request.GET.getlist('priority')
        if priority:
            queryset = queryset.filter(priority__in=priority)
        
        assigned_to = self.request.GET.get('assigned_to')
        if assigned_to:
            if assigned_to == 'unassigned':
                queryset = queryset.filter(assigned_to__isnull=True)
            else:
                queryset = queryset.filter(assigned_to_id=assigned_to)
        
        due_date_range = self.request.GET.get('due_date_range')
        today = date.today()
        if due_date_range:
            if due_date_range == 'overdue':
                queryset = queryset.filter(due_date__lt=today)
            elif due_date_range == 'today':
                queryset = queryset.filter(due_date=today)
            elif due_date_range == 'this_week':
                end_of_week = today + timedelta(days=(6 - today.weekday()))
                queryset = queryset.filter(due_date__gte=today, due_date__lte=end_of_week)
            elif due_date_range == 'next_week':
                start_of_next_week = today + timedelta(days=(7 - today.weekday()))
                end_of_next_week = start_of_next_week + timedelta(days=6)
                queryset = queryset.filter(due_date__gte=start_of_next_week, due_date__lte=end_of_next_week)
            elif due_date_range == 'this_month':
                next_month = today.replace(day=28) + timedelta(days=4)
                end_of_month = next_month - timedelta(days=next_month.day)
                queryset = queryset.filter(due_date__gte=today, due_date__lte=end_of_month)
            elif due_date_range == 'no_date':
                queryset = queryset.filter(due_date__isnull=True)
        
        return queryset.order_by('status', '-priority', 'due_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_department'] = 'arcade'
        
        # Get all arcade tasks for statistics
        all_arcade_tasks = GameTask.objects.filter(company_section='arcade')
        
        # Task statistics by status
        total_count = all_arcade_tasks.count()
        backlog_count = all_arcade_tasks.filter(status='backlog').count()
        to_do_count = all_arcade_tasks.filter(status='to_do').count()
        in_progress_count = all_arcade_tasks.filter(status='in_progress').count()
        in_review_count = all_arcade_tasks.filter(status='in_review').count()
        done_count = all_arcade_tasks.filter(status='done').count()
        blocked_count = all_arcade_tasks.filter(status='blocked').count()
        
        # Calculate percentages (rounded to nearest 10 for CSS classes)
        def calculate_percentage(count):
            if total_count == 0:
                return 0
            percentage = (count / total_count) * 100
            # Round to nearest 10 for CSS classes
            return round(percentage / 10) * 10
        
        task_stats = {
            'total': total_count,
            'backlog': backlog_count,
            'to_do': to_do_count,
            'in_progress': in_progress_count,
            'in_review': in_review_count,
            'done': done_count,
            'blocked': blocked_count,
            # Add percentages rounded to nearest 10 for CSS classes
            'backlog_percent': calculate_percentage(backlog_count),
            'to_do_percent': calculate_percentage(to_do_count),
            'in_progress_percent': calculate_percentage(in_progress_count),
            'in_review_percent': calculate_percentage(in_review_count),
            'done_percent': calculate_percentage(done_count),
            'blocked_percent': calculate_percentage(blocked_count),
        }
        
        context['task_stats'] = task_stats
        context['current_filters'] = dict(self.request.GET.items())
        
        return context
