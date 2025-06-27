"""
Views for handling Social Media tasks in the R1D3 system.
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

from .task_models import SocialMediaTask
from .task_forms import SocialMediaTaskForm
from django.contrib.auth.models import User


class SocialMediaTaskDashboardView(LoginRequiredMixin, ListView):
    """
    Dashboard view for social media tasks.
    """
    model = SocialMediaTask
    template_name = 'projects/social_media_task_dashboard.html'
    context_object_name = 'tasks'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Apply filters from GET parameters
        status_filter = self.request.GET.get('status')
        priority_filter = self.request.GET.get('priority')
        assigned_filter = self.request.GET.get('assigned_to')
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if priority_filter:
            queryset = queryset.filter(priority=priority_filter)
        if assigned_filter:
            queryset = queryset.filter(assigned_to=assigned_filter)
            
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
        
        # Add batch update URL
        context['batch_update_url'] = reverse('projects:social_media_task_batch_update')
        
        return context


class SocialMediaTaskCreateView(LoginRequiredMixin, CreateView):
    """
    Create a new social media task.
    """
    model = SocialMediaTask
    form_class = SocialMediaTaskForm
    template_name = 'projects/task_form.html'
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Social media task created successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('projects:social_media_task_dashboard')


class SocialMediaTaskDetailView(LoginRequiredMixin, DetailView):
    """
    View details of a social media task.
    """
    model = SocialMediaTask
    template_name = 'projects/task_detail.html'
    context_object_name = 'task'


class SocialMediaTaskUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Update an existing social media task.
    """
    model = SocialMediaTask
    form_class = SocialMediaTaskForm
    template_name = 'projects/task_form.html'
    
    def test_func(self):
        task = self.get_object()
        # Allow task creator, assigned user, or admin to edit
        return (self.request.user == task.created_by or 
                self.request.user == task.assigned_to or 
                self.request.user.is_staff)
    
    def form_valid(self, form):
        messages.success(self.request, 'Social media task updated successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('projects:social_media_task_detail', kwargs={'pk': self.object.pk})


class SocialMediaTaskDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Delete a social media task.
    """
    model = SocialMediaTask
    template_name = 'projects/task_confirm_delete.html'
    success_url = reverse_lazy('projects:social_media_task_dashboard')
    
    def test_func(self):
        task = self.get_object()
        # Only allow task creator or admin to delete
        return self.request.user == task.created_by or self.request.user.is_staff
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Social media task deleted successfully!')
        return super().delete(request, *args, **kwargs)


class SocialMediaTaskBatchUpdateView(LoginRequiredMixin, UpdateView):
    """
    Update multiple social media tasks at once via AJAX
    """
    model = SocialMediaTask
    form_class = SocialMediaTaskForm
    template_name = 'projects/social_media_task_form.html'
    
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
        tasks = SocialMediaTask.objects.filter(id__in=task_ids)
        
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


class SocialMediaTaskStatusUpdateView(LoginRequiredMixin, View):
    """
    Update the status of a social media task via AJAX
    """
    @method_decorator(require_POST)
    def post(self, request, *args, **kwargs):
        task_id = request.POST.get('task_id')
        new_status = request.POST.get('status')
        
        if not task_id or not new_status:
            return JsonResponse({'status': 'error', 'message': 'Task ID and status are required'})
        
        try:
            task = SocialMediaTask.objects.get(id=task_id)
            
            # Check if status is valid
            valid_statuses = [status[0] for status in SocialMediaTask.STATUS_CHOICES]
            if new_status not in valid_statuses:
                return JsonResponse({'status': 'error', 'message': 'Invalid status'})
            
            # Update status
            task.status = new_status
            task.save()
            
            return JsonResponse({
                'status': 'success',
                'message': f'Task status updated to {dict(SocialMediaTask.STATUS_CHOICES)[new_status]}',
                'new_status': new_status
            })
        except SocialMediaTask.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Task not found'})


class SocialMediaTaskHoursUpdateView(LoginRequiredMixin, View):
    """
    Update the actual hours of a social media task via AJAX
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
                
            task = SocialMediaTask.objects.get(id=task_id)
            task.actual_hours = hours
            task.save()
            
            return JsonResponse({
                'status': 'success',
                'message': f'Task hours updated to {hours}',
                'hours': hours
            })
        except ValueError:
            return JsonResponse({'status': 'error', 'message': 'Invalid hours value'})
        except SocialMediaTask.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Task not found'})


def create_sample_social_media_tasks():
    """
    Create sample social media tasks for demonstration purposes.
    """
    # Get or create a user
    user, created = User.objects.get_or_create(
        username='admin',
        defaults={'email': 'admin@example.com', 'is_staff': True}
    )
    
    # Create sample tasks
    sample_tasks = [
        {
            'title': 'Create Instagram content calendar',
            'description': 'Plan and create a content calendar for Instagram posts for the next month',
            'task_type': 'content',
            'status': 'to_do',
            'priority': 'high',
            'assigned_to': user,
            'due_date': date.today() + timedelta(days=7),
            'estimated_hours': 4,
            'campaign_id': 'INSTA-2023-Q2',
            'channel': 'instagram',
            'target_metrics': 'Engagement rate: 5%, Followers: +500'
        },
        {
            'title': 'Twitter campaign for game launch',
            'description': 'Create and schedule tweets for the upcoming game launch',
            'task_type': 'marketing',
            'status': 'in_progress',
            'priority': 'critical',
            'assigned_to': user,
            'due_date': date.today() + timedelta(days=3),
            'estimated_hours': 6,
            'campaign_id': 'GAME-LAUNCH-2023',
            'channel': 'twitter',
            'target_metrics': 'Impressions: 10K, Clicks: 500'
        },
        {
            'title': 'Monthly social media analytics report',
            'description': 'Compile and analyze social media performance across all channels',
            'task_type': 'reporting',
            'status': 'to_do',
            'priority': 'medium',
            'assigned_to': user,
            'due_date': date.today() + timedelta(days=14),
            'estimated_hours': 3,
            'campaign_id': 'MONTHLY-ANALYTICS',
            'channel': 'all',
            'target_metrics': 'N/A'
        }
    ]
    
    for task_data in sample_tasks:
        SocialMediaTask.objects.get_or_create(
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
                'campaign_id': task_data['campaign_id'],
                'channel': task_data['channel'],
                'target_metrics': task_data['target_metrics']
            }
        )
