from django.shortcuts import render, redirect
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView, DetailView
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import JsonResponse
from datetime import date, timedelta
import json

from projects.task_models import ThemeParkTask
from django.contrib.auth.models import User


class ThemeParkDashboardView(LoginRequiredMixin, TemplateView):
    """Dashboard view for the Theme Park department"""
    template_name = 'theme_park/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_department'] = 'theme_park'
        return context


class ParkProjectsView(LoginRequiredMixin, TemplateView):
    """View for managing theme park projects"""
    template_name = 'theme_park/projects.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_department'] = 'theme_park'
        return context


class AttractionsView(LoginRequiredMixin, TemplateView):
    """View for managing theme park attractions"""
    template_name = 'theme_park/attractions.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_department'] = 'theme_park'
        return context


class ParkMapView(LoginRequiredMixin, TemplateView):
    """View for theme park map"""
    template_name = 'theme_park/map.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_department'] = 'theme_park'
        return context


class ThemeParkTasksView(LoginRequiredMixin, ListView):
    """View for theme park department tasks"""
    model = ThemeParkTask
    template_name = 'theme_park/tasks.html'
    context_object_name = 'theme_park_tasks'
    
    def get_queryset(self):
        # Get all theme park tasks
        queryset = ThemeParkTask.objects.all()
        print(f"DEBUG: Found {queryset.count()} theme park tasks")
        # Print first 5 tasks for debugging
        for task in queryset[:5]:
            print(f"DEBUG: Task ID: {task.id}, Title: {task.title}, Status: {task.status}")
        
        # Apply filters from request parameters
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
            
        priority = self.request.GET.get('priority')
        if priority:
            queryset = queryset.filter(priority=priority)
            
        attraction_id = self.request.GET.get('attraction_id')
        if attraction_id:
            queryset = queryset.filter(attraction_id=attraction_id)
            
        zone = self.request.GET.get('zone')
        if zone:
            queryset = queryset.filter(zone=zone)
            
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
        context['active_department'] = 'theme_park'
        
        # Get all theme park tasks for statistics
        all_theme_park_tasks = ThemeParkTask.objects.all()
        today = date.today()
        
        # Task statistics by status
        total_count = all_theme_park_tasks.count()
        backlog_count = all_theme_park_tasks.filter(status='backlog').count()
        to_do_count = all_theme_park_tasks.filter(status='to_do').count()
        in_progress_count = all_theme_park_tasks.filter(status='in_progress').count()
        in_review_count = all_theme_park_tasks.filter(status='in_review').count()
        done_count = all_theme_park_tasks.filter(status='done').count()
        blocked_count = all_theme_park_tasks.filter(status='blocked').count()
        
        # Additional statistics for dashboard cards
        overdue_count = all_theme_park_tasks.filter(due_date__lt=today).exclude(status='done').count()
        completed_this_week = all_theme_park_tasks.filter(
            status='done',
            updated_at__gte=today - timedelta(days=today.weekday())
        ).count()
        
        # Calculate percentages
        def calculate_percentage(count):
            if total_count == 0:
                return 0
            percentage = (count / total_count) * 100
            # Round to nearest integer for better display
            return round(percentage)
        
        task_stats = {
            'total': total_count,
            'backlog': backlog_count,
            'to_do': to_do_count,
            'in_progress': in_progress_count,
            'in_review': in_review_count,
            'done': done_count,
            'blocked': blocked_count,
            'overdue': overdue_count,
            'completed_this_week': completed_this_week,
            # Add percentages
            'backlog_percent': calculate_percentage(backlog_count),
            'to_do_percent': calculate_percentage(to_do_count),
            'in_progress_percent': calculate_percentage(in_progress_count),
            'in_review_percent': calculate_percentage(in_review_count),
            'done_percent': calculate_percentage(done_count),
            'blocked_percent': calculate_percentage(blocked_count),
            'overdue_percent': calculate_percentage(overdue_count),
            'completed_percent': calculate_percentage(completed_this_week),
        }
        
        context['task_stats'] = task_stats
        
        # Get distinct attractions from theme park tasks
        attractions = ThemeParkTask.objects.values('attraction_id').annotate(
            count=Count('id')
        ).order_by('attraction_id')
        
        # Format attractions for template
        formatted_attractions = []
        for attraction in attractions:
            if attraction['attraction_id']:
                formatted_attractions.append({
                    'id': attraction['attraction_id'],
                    'title': attraction['attraction_id'],
                    'count': attraction['count']
                })
        context['attractions'] = formatted_attractions
        
        # Get distinct zones from theme park tasks
        zones = ThemeParkTask.objects.values('zone').annotate(
            count=Count('id')
        ).order_by('zone')
        
        # Format zones for template
        formatted_zones = []
        for zone in zones:
            if zone['zone']:
                formatted_zones.append({
                    'id': zone['zone'],
                    'title': zone['zone'],
                    'count': zone['count']
                })
        context['zones'] = formatted_zones
        
        # Get all users for assignment filter
        context['users'] = User.objects.filter(is_active=True).order_by('first_name', 'last_name')
        
        # Add today's date for due date comparisons
        context['today'] = date.today()
        
        # Check if filters are applied
        context['current_filters'] = any([
            self.request.GET.get('status'),
            self.request.GET.get('priority'),
            self.request.GET.get('attraction_id'),
            self.request.GET.get('zone'),
            self.request.GET.get('assigned_to'),
            self.request.GET.get('due_date_range')
        ])
        
        return context


class ThemeParkTaskCreateView(LoginRequiredMixin, CreateView):
    """View for creating new theme park tasks"""
    model = ThemeParkTask
    template_name = 'theme_park/task_form.html'
    from projects.task_forms import ThemeParkTaskForm
    form_class = ThemeParkTaskForm
    success_url = reverse_lazy('theme_park:tasks')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.company_section = 'theme_park'
        messages.success(self.request, 'Theme park task created successfully!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_department'] = 'theme_park'
        context['form_title'] = 'Create New Theme Park Task'
        context['submit_text'] = 'Create Task'
        return context


class ThemeParkTaskDetailView(LoginRequiredMixin, DetailView):
    """View for viewing theme park task details"""
    model = ThemeParkTask
    template_name = 'theme_park/task_detail.html'
    context_object_name = 'task'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_department'] = 'theme_park'
        context['today'] = date.today()
        return context


class ThemeParkTaskUpdateView(LoginRequiredMixin, UpdateView):
    """View for updating theme park tasks"""
    model = ThemeParkTask
    template_name = 'theme_park/task_form.html'
    from projects.task_forms import ThemeParkTaskForm
    form_class = ThemeParkTaskForm
    success_url = reverse_lazy('theme_park:tasks')
    
    def form_valid(self, form):
        messages.success(self.request, 'Theme park task updated successfully!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_department'] = 'theme_park'
        context['form_title'] = 'Update Theme Park Task'
        context['submit_text'] = 'Update Task'
        return context


class ThemeParkTaskDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """View for deleting theme park tasks"""
    model = ThemeParkTask
    template_name = 'projects/task_confirm_delete.html'
    success_url = reverse_lazy('theme_park:tasks')
    
    def test_func(self):
        task = self.get_object()
        # Only allow task creator or admin to delete
        return self.request.user == task.created_by or self.request.user.is_staff
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Theme park task deleted successfully!')
        return super().delete(request, *args, **kwargs)


class ThemeParkTaskStatusUpdateView(LoginRequiredMixin, View):
    """View for updating theme park task status"""
    
    def post(self, request, pk):
        task = ThemeParkTask.objects.get(pk=pk)
        status = request.POST.get('status')
        
        if status:
            task.status = status
            task.save()
            messages.success(request, f'Task status updated to {task.get_status_display()}')
        
        return redirect('theme_park:task_detail', pk=task.id)


class ThemeParkTaskHoursUpdateView(LoginRequiredMixin, View):
    """View for updating theme park task hours"""
    
    def post(self, request, pk):
        task = ThemeParkTask.objects.get(pk=pk)
        actual_hours = request.POST.get('actual_hours')
        
        if actual_hours:
            try:
                task.actual_hours = float(actual_hours)
                task.save()
                messages.success(request, f'Task hours updated to {task.actual_hours}')
            except ValueError:
                messages.error(request, 'Invalid hours value')
        
        return redirect('theme_park:task_detail', pk=task.id)


class ThemeParkTaskBatchUpdateView(LoginRequiredMixin, View):
    """View for batch updating theme park tasks"""
    
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            task_ids = data.get('task_ids', [])
            
            if not task_ids:
                return JsonResponse({'status': 'error', 'message': 'No tasks selected'}, status=400)
            
            # Fields to update
            fields_to_update = {}
            if data.get('status'):
                fields_to_update['status'] = data['status']
            if data.get('priority'):
                fields_to_update['priority'] = data['priority']
            if data.get('zone'):
                fields_to_update['zone'] = data['zone']
            if data.get('assigned_to'):
                fields_to_update['assigned_to_id'] = data['assigned_to']
            if data.get('due_date'):
                fields_to_update['due_date'] = data['due_date']
            
            if not fields_to_update:
                return JsonResponse({'status': 'error', 'message': 'No fields selected for update'}, status=400)
            
            # Update tasks
            updated_count = ThemeParkTask.objects.filter(id__in=task_ids).update(**fields_to_update)
            
            return JsonResponse({
                'status': 'success',
                'message': f'Successfully updated {updated_count} tasks',
                'updated_count': updated_count
            })
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
