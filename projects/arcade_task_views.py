"""
Views for handling Arcade tasks in the R1D3 system.
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

from .task_models import ArcadeTask
from .task_forms import ArcadeTaskForm
from django.contrib.auth.models import User


class ArcadeTaskDashboardView(LoginRequiredMixin, ListView):
    """
    Dashboard view for arcade tasks.
    """
    model = ArcadeTask
    template_name = 'projects/arcade_task_dashboard.html'
    context_object_name = 'tasks'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Apply filters from GET parameters
        status_filter = self.request.GET.get('status')
        priority_filter = self.request.GET.get('priority')
        assigned_filter = self.request.GET.get('assigned_to')
        location_filter = self.request.GET.get('location')
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if priority_filter:
            queryset = queryset.filter(priority=priority_filter)
        if assigned_filter:
            queryset = queryset.filter(assigned_to=assigned_filter)
        if location_filter:
            queryset = queryset.filter(location=location_filter)
            
        return queryset.order_by('-priority', 'status', 'due_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add status counts
        queryset = self.get_queryset()
        status_counts = {}
        for status_code, status_name in self.model.STATUS_CHOICES:
            status_counts[status_code] = queryset.filter(status=status_code).count()
        context['status_counts'] = status_counts
        context['today'] = date.today()
        
        # Add users for filtering
        context['users'] = User.objects.all()
        
        # Add locations for filtering
        context['locations'] = ArcadeTask.objects.values_list('location', flat=True).distinct()
        
        # Add batch update URL
        context['batch_update_url'] = reverse('projects:arcade_task_batch_update')
        
        return context


class ArcadeTaskCreateView(LoginRequiredMixin, CreateView):
    """
    Create a new arcade task.
    """
    model = ArcadeTask
    form_class = ArcadeTaskForm
    template_name = 'projects/arcade_task_form.html'
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Arcade task created successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('projects:arcade_task_dashboard')


class ArcadeTaskDetailView(LoginRequiredMixin, DetailView):
    """
    View details of an arcade task.
    """
    model = ArcadeTask
    template_name = 'projects/task_detail.html'
    context_object_name = 'task'


class ArcadeTaskUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Update an existing arcade task.
    """
    model = ArcadeTask
    form_class = ArcadeTaskForm
    template_name = 'projects/arcade_task_form.html'
    
    def test_func(self):
        task = self.get_object()
        # Allow task creator, assigned user, or admin to edit
        return (self.request.user == task.created_by or 
                self.request.user == task.assigned_to or 
                self.request.user.is_staff)
    
    def form_valid(self, form):
        messages.success(self.request, 'Arcade task updated successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('projects:arcade_task_detail', kwargs={'pk': self.object.pk})


class ArcadeTaskDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Delete an arcade task.
    """
    model = ArcadeTask
    template_name = 'projects/task_confirm_delete.html'
    success_url = reverse_lazy('projects:arcade_task_dashboard')
    
    def test_func(self):
        task = self.get_object()
        # Only allow task creator or admin to delete
        return self.request.user == task.created_by or self.request.user.is_staff
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Arcade task deleted successfully!')
        return super().delete(request, *args, **kwargs)


class ArcadeTaskBatchUpdateView(LoginRequiredMixin, UpdateView):
    """
    Update multiple arcade tasks at once via AJAX
    """
    model = ArcadeTask
    form_class = ArcadeTaskForm
    template_name = 'projects/arcade_task_form.html'
    
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
        tasks = ArcadeTask.objects.filter(id__in=task_ids)
        
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


class ArcadeTaskStatusUpdateView(LoginRequiredMixin, View):
    """
    Update the status of an arcade task via AJAX
    """
    @method_decorator(require_POST)
    def post(self, request, *args, **kwargs):
        task_id = request.POST.get('task_id')
        new_status = request.POST.get('status')
        
        if not task_id or not new_status:
            return JsonResponse({'status': 'error', 'message': 'Task ID and status are required'})
        
        try:
            task = ArcadeTask.objects.get(id=task_id)
            
            # Check if status is valid
            valid_statuses = [status[0] for status in ArcadeTask.STATUS_CHOICES]
            if new_status not in valid_statuses:
                return JsonResponse({'status': 'error', 'message': 'Invalid status'})
            
            # Update status
            task.status = new_status
            task.save()
            
            return JsonResponse({
                'status': 'success',
                'message': f'Task status updated to {dict(ArcadeTask.STATUS_CHOICES)[new_status]}',
                'new_status': new_status
            })
        except ArcadeTask.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Task not found'})


class ArcadeTaskHoursUpdateView(LoginRequiredMixin, View):
    """
    Update the actual hours of an arcade task via AJAX
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
                
            task = ArcadeTask.objects.get(id=task_id)
            task.actual_hours = hours
            task.save()
            
            return JsonResponse({
                'status': 'success',
                'message': f'Task hours updated to {hours}',
                'hours': hours
            })
        except ValueError:
            return JsonResponse({'status': 'error', 'message': 'Invalid hours value'})
        except ArcadeTask.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Task not found'})


def create_sample_arcade_tasks():
    """
    Create sample arcade tasks for demonstration purposes.
    """
    # Get or create a user
    user, created = User.objects.get_or_create(
        username='admin',
        defaults={'email': 'admin@example.com', 'is_staff': True}
    )
    
    # Create sample tasks
    sample_tasks = [
        {
            'title': 'Repair Pac-Man machine',
            'description': 'Fix joystick and replace coin mechanism on Pac-Man arcade cabinet',
            'task_type': 'maintenance',
            'status': 'to_do',
            'priority': 'high',
            'assigned_to': user,
            'due_date': date.today() + timedelta(days=2),
            'estimated_hours': 3,
            'machine_id': 'PAC-001',
            'location': 'Main Floor',
            'maintenance_type': 'repair'
        },
        {
            'title': 'Install new Street Fighter cabinet',
            'description': 'Unbox, assemble, and test new Street Fighter arcade machine',
            'task_type': 'installation',
            'status': 'in_progress',
            'priority': 'critical',
            'assigned_to': user,
            'due_date': date.today() + timedelta(days=1),
            'estimated_hours': 5,
            'machine_id': 'SF-2023-01',
            'location': 'Competition Area',
            'maintenance_type': 'installation'
        },
        {
            'title': 'Weekly cleaning of racing simulators',
            'description': 'Clean and sanitize all racing simulator cabinets and controls',
            'task_type': 'maintenance',
            'status': 'recurring',
            'priority': 'medium',
            'assigned_to': user,
            'due_date': date.today() + timedelta(days=7),
            'estimated_hours': 2,
            'machine_id': 'RACE-ALL',
            'location': 'Racing Zone',
            'maintenance_type': 'cleaning'
        }
    ]
    
    for task_data in sample_tasks:
        ArcadeTask.objects.get_or_create(
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
                'machine_id': task_data['machine_id'],
                'location': task_data['location'],
                'maintenance_type': task_data['maintenance_type']
            }
        )
