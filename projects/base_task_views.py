from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import date

class BaseTaskListView(LoginRequiredMixin, ListView):
    """
    Base class for all task list views
    """
    template_name = 'projects/task_list.html'
    context_object_name = 'tasks'
    paginate_by = 20
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['today'] = date.today()
        
        # Add status and priority choices for filtering
        model_class = self.model
        context['status_choices'] = model_class.STATUS_CHOICES
        context['priority_choices'] = model_class.PRIORITY_CHOICES
        
        # Add task counts by status
        queryset = self.get_queryset()
        status_counts = {}
        for status_code, status_name in model_class.STATUS_CHOICES:
            status_counts[status_code] = queryset.filter(status=status_code).count()
        context['status_counts'] = status_counts
        
        # Add overdue tasks count
        context['overdue_count'] = queryset.filter(
            due_date__lt=timezone.now().date(),
            status__in=['to_do', 'in_progress', 'blocked']
        ).count()
        
        return context


class BaseTaskDetailView(LoginRequiredMixin, DetailView):
    """
    Base class for all task detail views
    """
    template_name = 'projects/task_detail.html'
    context_object_name = 'task'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['today'] = date.today()
        
        # Add status and priority choices for status changes
        model_class = self.model
        context['status_choices'] = model_class.STATUS_CHOICES
        context['priority_choices'] = model_class.PRIORITY_CHOICES
        
        # Check if the user can edit this task
        user = self.request.user
        task = self.object
        context['can_edit'] = (
            user.is_staff or 
            user == task.created_by or 
            user == task.assigned_to
        )
        
        return context


class BaseTaskCreateView(LoginRequiredMixin, CreateView):
    """
    Base class for all task create views
    """
    template_name = 'projects/task_form.html'
    
    def get_success_url(self):
        """Default success URL - override in subclasses if needed"""
        messages.success(self.request, f"Task '{self.object.title}' created successfully!")
        return reverse_lazy('tasks:task_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['today'] = date.today()
        context['is_create'] = True
        return context


class BaseTaskUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Base class for all task update views
    """
    template_name = 'projects/task_form.html'
    
    def test_func(self):
        """Only allow staff, creator or assignee to update the task"""
        user = self.request.user
        task = self.get_object()
        return user.is_staff or user == task.created_by or user == task.assigned_to
    
    def get_success_url(self):
        """Default success URL - override in subclasses if needed"""
        messages.success(self.request, f"Task '{self.object.title}' updated successfully!")
        return reverse_lazy('tasks:task_detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['today'] = date.today()
        context['is_update'] = True
        return context


class BaseTaskDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Base class for all task delete views
    """
    template_name = 'projects/task_confirm_delete.html'
    context_object_name = 'task'
    
    def test_func(self):
        """Only allow staff, creator or assignee to delete the task"""
        user = self.request.user
        task = self.get_object()
        return user.is_staff or user == task.created_by
    
    def get_success_url(self):
        """Default success URL - override in subclasses if needed"""
        messages.success(self.request, f"Task '{self.object.title}' deleted successfully!")
        return reverse_lazy('tasks:task_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['today'] = date.today()
        return context


class BaseTaskKanbanView(LoginRequiredMixin, ListView):
    """
    Base class for all task kanban views
    """
    template_name = 'projects/task_kanban.html'
    context_object_name = 'tasks'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['today'] = date.today()
        
        # Group tasks by status for kanban columns
        model_class = self.model
        tasks_by_status = {}
        for status, label in model_class.STATUS_CHOICES:
            tasks_by_status[status] = self.get_queryset().filter(status=status).order_by('-priority', 'due_date')
        
        context['tasks_by_status'] = tasks_by_status
        context['status_choices'] = model_class.STATUS_CHOICES
        
        return context
