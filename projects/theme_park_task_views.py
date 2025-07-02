"""
Views for handling Theme Park tasks in the R1D3 system.
"""
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.shortcuts import redirect
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
import json
from datetime import date, timedelta

from .task_models import ThemeParkTask
from .task_forms import ThemeParkTaskForm
from django.contrib.auth.models import User


class ThemeParkTaskDashboardView(LoginRequiredMixin, ListView):
    """
    Dashboard view for theme park tasks.
    """
    model = ThemeParkTask
    template_name = 'projects/theme_park_task_dashboard.html'
    context_object_name = 'tasks'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Apply filters from GET parameters
        status_filter = self.request.GET.get('status')
        priority_filter = self.request.GET.get('priority')
        assigned_filter = self.request.GET.get('assigned_to')
        area_filter = self.request.GET.get('area')
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if priority_filter:
            queryset = queryset.filter(priority=priority_filter)
        if assigned_filter:
            queryset = queryset.filter(assigned_to=assigned_filter)
        if area_filter:
            queryset = queryset.filter(area=area_filter)
            
        return queryset.order_by('-priority', 'status', 'due_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add status counts
        queryset = self.get_queryset()
        status_counts = {}
        total_tasks = queryset.count() or 1  # Avoid division by zero
        
        for status_code, status_name in self.model.STATUS_CHOICES:
            count = queryset.filter(status=status_code).count()
            status_counts[status_code] = count
            # Calculate percentage for progress bars and format as CSS-compatible string
            status_counts[f'{status_code}_percent'] = f'{int((count / total_tasks) * 100)}%'
            
        context['status_counts'] = status_counts
        context['today'] = date.today()
        
        # Add users for filtering
        context['users'] = User.objects.all()
        
        # Add areas for filtering
        context['areas'] = ThemeParkTask.objects.values_list('area', flat=True).distinct()
        
        # Add batch update URL
        context['batch_update_url'] = reverse('projects:theme_park_task_batch_update')
        
        return context


class ThemeParkTaskCreateView(LoginRequiredMixin, CreateView):
    """
    Create a new theme park task.
    """
    model = ThemeParkTask
    form_class = ThemeParkTaskForm
    template_name = 'projects/theme_park_task_form.html'
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Theme park task created successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('projects:theme_park_task_dashboard')


class ThemeParkTaskDetailView(LoginRequiredMixin, DetailView):
    """
    View details of a theme park task.
    """
    model = ThemeParkTask
    template_name = 'projects/task_detail.html'
    context_object_name = 'task'


class ThemeParkTaskUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Update an existing theme park task.
    """
    model = ThemeParkTask
    form_class = ThemeParkTaskForm
    template_name = 'projects/theme_park_task_form.html'
    
    def test_func(self):
        task = self.get_object()
        # Allow task creator, assigned user, or admin to edit
        return (self.request.user == task.created_by or 
                self.request.user == task.assigned_to or 
                self.request.user.is_staff)
    
    def form_valid(self, form):
        messages.success(self.request, 'Theme park task updated successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('projects:theme_park_task_detail', kwargs={'pk': self.object.pk})


class ThemeParkTaskDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Delete a theme park task.
    """
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


class ThemeParkTaskBatchUpdateView(LoginRequiredMixin, UpdateView):
    """
    Update multiple theme park tasks at once via AJAX
    """
    model = ThemeParkTask
    form_class = ThemeParkTaskForm
    template_name = 'projects/theme_park_task_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_batch_update'] = True
        return context
    
    @method_decorator(require_POST)
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        task_ids = data.get('task_ids', [])
        update_data = data.get('update_data', {})
        
        # Remove empty fields
        update_data = {k: v for k, v in update_data.items() if v}
        
        if not task_ids or not update_data:
            return JsonResponse({'status': 'error', 'message': 'No tasks or update data provided'})
        
        # Get tasks to update
        tasks = ThemeParkTask.objects.filter(id__in=task_ids)
        
        # Handle special fields
        if 'assigned_to' in update_data and update_data['assigned_to']:
            try:
                user = User.objects.get(id=update_data['assigned_to'])
                update_data['assigned_to'] = user
            except User.DoesNotExist:
                del update_data['assigned_to']
        
        # Update tasks
        updated_count = 0
        for task in tasks:
            for field, value in update_data.items():
                setattr(task, field, value)
            task.save()
            updated_count += 1
        
        return JsonResponse({
            'status': 'success',
            'message': f'Updated {updated_count} tasks successfully',
            'updated_count': updated_count
        })


class ThemeParkTaskStatusUpdateView(LoginRequiredMixin, View):
    """
    Update the status of a theme park task via AJAX
    """
    @method_decorator(require_POST)
    def post(self, request, *args, **kwargs):
        task_id = request.POST.get('task_id')
        new_status = request.POST.get('status')
        
        if not task_id or not new_status:
            return JsonResponse({'status': 'error', 'message': 'Task ID and status are required'})
        
        try:
            task = ThemeParkTask.objects.get(id=task_id)
            
            # Check if status is valid
            valid_statuses = [status[0] for status in ThemeParkTask.STATUS_CHOICES]
            if new_status not in valid_statuses:
                return JsonResponse({'status': 'error', 'message': 'Invalid status'})
            
            # Update status
            task.status = new_status
            task.save()
            
            return JsonResponse({
                'status': 'success',
                'message': f'Task status updated to {dict(ThemeParkTask.STATUS_CHOICES)[new_status]}',
                'new_status': new_status
            })
        except ThemeParkTask.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Task not found'})


class ThemeParkTaskHoursUpdateView(LoginRequiredMixin, View):
    """
    Update the actual hours of a theme park task via AJAX
    """
    @method_decorator(require_POST)
    def post(self, request, *args, **kwargs):
        task_id = request.POST.get('task_id')
        hours = request.POST.get('hours')
        
        if not task_id or hours is None:
            return JsonResponse({'status': 'error', 'message': 'Task ID and hours are required'})
        
        try:
            hours = float(hours)
            if hours < 0:
                return JsonResponse({'status': 'error', 'message': 'Hours cannot be negative'})
                
            task = ThemeParkTask.objects.get(id=task_id)
            task.actual_hours = hours
            task.save()
            
            return JsonResponse({
                'status': 'success',
                'message': f'Task hours updated to {hours}',
                'hours': hours
            })
        except ValueError:
            return JsonResponse({'status': 'error', 'message': 'Invalid hours value'})
        except ThemeParkTask.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Task not found'})


def create_sample_theme_park_tasks():
    """
    Create sample theme park tasks for demonstration purposes.
    """
    # Get or create a user
    user, created = User.objects.get_or_create(
        username='admin',
        defaults={'email': 'admin@example.com', 'is_staff': True}
    )
    
    # Create sample tasks
    sample_tasks = [
        {
            'title': 'Roller Coaster Safety Inspection',
            'description': 'Conduct monthly safety inspection of the Thunderbolt roller coaster',
            'task_type': 'maintenance',
            'status': 'to_do',
            'priority': 'critical',
            'assigned_to': user,
            'due_date': date.today() + timedelta(days=3),
            'estimated_hours': 6,
            'attraction_id': 'THUNDER-001',
            'area': 'Thrill Zone',
            'maintenance_type': 'safety_inspection'
        },
        {
            'title': 'Water Ride Seasonal Preparation',
            'description': 'Prepare the Splash Canyon water ride for summer season opening',
            'task_type': 'maintenance',
            'status': 'in_progress',
            'priority': 'high',
            'assigned_to': user,
            'due_date': date.today() + timedelta(days=14),
            'estimated_hours': 24,
            'attraction_id': 'SPLASH-002',
            'area': 'Water World',
            'maintenance_type': 'seasonal_prep'
        },
        {
            'title': 'Food Court Renovation Planning',
            'description': 'Create plans for renovating the main food court area',
            'task_type': 'planning',
            'status': 'to_do',
            'priority': 'medium',
            'assigned_to': user,
            'due_date': date.today() + timedelta(days=30),
            'estimated_hours': 10,
            'attraction_id': 'FOOD-MAIN',
            'area': 'Central Plaza',
            'maintenance_type': 'renovation'
        }
    ]
    
    for task_data in sample_tasks:
        ThemeParkTask.objects.get_or_create(
            title=task_data['title'],
            defaults={
                'description': task_data['description'],
                'task_type': task_data['task_type'],
                'status': task_data['status'],
                'priority': task_data['priority'],
                'assigned_to': task_data['assigned_to'],
                'due_date': task_data['due_date'],
                'estimated_hours': task_data['estimated_hours'],
                'created_by': user,
                'attraction_id': task_data['attraction_id'],
                'area': task_data['area'],
                'maintenance_type': task_data['maintenance_type']
            }
        )
