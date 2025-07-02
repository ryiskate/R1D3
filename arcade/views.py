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

from projects.game_models import GameTask
from projects.task_models import ArcadeTask
from django.contrib.auth.models import User


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
    model = ArcadeTask
    template_name = 'arcade/tasks.html'
    context_object_name = 'arcade_tasks'
    
    def get_queryset(self):
        queryset = ArcadeTask.objects.all()
        
        # Apply filters from request parameters
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
            
        priority = self.request.GET.get('priority')
        if priority:
            queryset = queryset.filter(priority=priority)
            
        machine_id = self.request.GET.get('machine_id')
        if machine_id:
            queryset = queryset.filter(machine_id=machine_id)
            
        location = self.request.GET.get('location')
        if location:
            queryset = queryset.filter(location=location)
            
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
        
        # Add today's date for due date comparisons
        context['today'] = date.today()
        
        return context


class ArcadeTaskDetailView(LoginRequiredMixin, DetailView):
    """View for viewing arcade task details"""
    model = ArcadeTask
    template_name = 'arcade/task_detail.html'
    context_object_name = 'task'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_department'] = 'arcade'
        context['today'] = date.today()
        return context


class ArcadeTaskUpdateView(LoginRequiredMixin, UpdateView):
    """View for updating arcade tasks"""
    model = ArcadeTask
    template_name = 'arcade/task_form.html'
    from projects.task_forms import ArcadeTaskForm
    form_class = ArcadeTaskForm
    success_url = reverse_lazy('arcade:tasks')
    
    def form_valid(self, form):
        messages.success(self.request, 'Arcade task updated successfully!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_department'] = 'arcade'
        context['title'] = 'Update Arcade Task'
        return context


class ArcadeTaskDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """View for deleting arcade tasks"""
    model = ArcadeTask
    template_name = 'arcade/task_confirm_delete.html'
    context_object_name = 'task'  # Explicitly set the context object name
    success_url = reverse_lazy('arcade:tasks')
    
    def test_func(self):
        task = self.get_object()
        # Only allow task creator or admin to delete
        return self.request.user == task.created_by or self.request.user.is_staff
    
    def delete(self, request, *args, **kwargs):
        task = self.get_object()
        task_title = task.title  # Store the title before deletion
        messages.success(request, f'Arcade task "{task_title}" deleted successfully!')
        return super().delete(request, *args, **kwargs)
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_department'] = 'arcade'
        return context


class ArcadeTaskStatusUpdateView(LoginRequiredMixin, View):
    """View for updating arcade task status"""
    
    def post(self, request, pk):
        task = ArcadeTask.objects.get(pk=pk)
        status = request.POST.get('status')
        
        if status:
            task.status = status
            task.save()
            messages.success(request, f'Task status updated to {task.get_status_display()}')
        
        return redirect('arcade:task_detail', pk=task.id)


class ArcadeTaskHoursUpdateView(LoginRequiredMixin, View):
    """View for updating arcade task hours"""
    
    def post(self, request, pk):
        task = ArcadeTask.objects.get(pk=pk)
        actual_hours = request.POST.get('actual_hours')
        
        if actual_hours:
            try:
                task.actual_hours = float(actual_hours)
                task.save()
                messages.success(request, f'Task hours updated to {task.actual_hours}')
            except ValueError:
                messages.error(request, 'Invalid hours value')
        
        return redirect('arcade:task_detail', pk=task.id)


class ArcadeTaskBatchUpdateView(LoginRequiredMixin, View):
    """View for batch updating arcade tasks"""
    
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
            if data.get('location'):
                fields_to_update['location'] = data['location']
            if data.get('assigned_to'):
                fields_to_update['assigned_to_id'] = data['assigned_to']
            if data.get('due_date'):
                fields_to_update['due_date'] = data['due_date']
            
            if not fields_to_update:
                return JsonResponse({'status': 'error', 'message': 'No fields selected for update'}, status=400)
            
            # Update tasks
            updated_count = ArcadeTask.objects.filter(id__in=task_ids).update(**fields_to_update)
            
            return JsonResponse({
                'status': 'success',
                'message': f'Successfully updated {updated_count} tasks',
                'updated_count': updated_count
            })
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


class ArcadeTaskCreateView(LoginRequiredMixin, CreateView):
    """View for creating arcade tasks"""
    model = ArcadeTask
    template_name = 'arcade/task_form.html'
    from projects.task_forms import ArcadeTaskForm
    form_class = ArcadeTaskForm
    success_url = reverse_lazy('arcade:tasks')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Arcade task created successfully!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_department'] = 'arcade'
        context['users'] = User.objects.all()
        context['is_create'] = True
        return context
