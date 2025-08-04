from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import date
from .task_models import SubTask
import json

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
        
        # Get subtasks if the task has them
        if task.has_subtasks:
            content_type = ContentType.objects.get_for_model(task)
            subtasks = SubTask.objects.filter(
                content_type=content_type,
                object_id=task.id
            )
            context['subtasks'] = subtasks
        
        return context


class BaseTaskCreateView(LoginRequiredMixin, CreateView):
    """
    Base class for all task create views
    """
    template_name = 'projects/unified_task_form.html'
    
    def form_valid(self, form):
        # Set the created_by field to the current user
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        
        # Process subtasks if they exist
        if form.instance.has_subtasks and 'subtasks' in self.request.POST:
            subtasks_data = self.request.POST.getlist('subtasks')
            content_type = ContentType.objects.get_for_model(self.object)
            
            for subtask_json in subtasks_data:
                try:
                    subtask_data = json.loads(subtask_json)
                    if subtask_data.get('title'):
                        SubTask.objects.create(
                            content_type=content_type,
                            object_id=self.object.id,
                            title=subtask_data.get('title'),
                            is_completed=subtask_data.get('is_completed', False)
                        )
                except json.JSONDecodeError:
                    pass  # Skip invalid JSON data
        
        return response
    
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
    template_name = 'projects/unified_task_form.html'
    
    def test_func(self):
        """Only allow staff, creator or assignee to update the task"""
        user = self.request.user
        task = self.get_object()
        return user.is_staff or user == task.created_by or user == task.assigned_to
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Get the content type for the task model
        content_type = ContentType.objects.get_for_model(self.object)
        
        # Delete existing subtasks if the checkbox is unchecked
        if not form.instance.has_subtasks:
            SubTask.objects.filter(
                content_type=content_type,
                object_id=self.object.id
            ).delete()
        # Update existing subtasks
        elif 'subtasks' in self.request.POST:
            # First delete all existing subtasks
            SubTask.objects.filter(
                content_type=content_type,
                object_id=self.object.id
            ).delete()
            
            # Then create new ones from the form data
            subtasks_data = self.request.POST.getlist('subtasks')
            
            # Debug print
            print("Raw subtasks data from form:")
            for subtask_json in subtasks_data:
                print(subtask_json)
                try:
                    subtask_data = json.loads(subtask_json)
                    print(f"Parsed JSON: {subtask_data}")
                    print(f"is_completed value: {subtask_data.get('is_completed', 'NOT FOUND')}")
                except json.JSONDecodeError:
                    print(f"Invalid JSON: {subtask_json}")
            
            for subtask_json in subtasks_data:
                try:
                    subtask_data = json.loads(subtask_json)
                    if subtask_data.get('title'):
                        SubTask.objects.create(
                            content_type=content_type,
                            object_id=self.object.id,
                            title=subtask_data.get('title'),
                            is_completed=subtask_data.get('is_completed', False)
                        )
                except json.JSONDecodeError:
                    pass  # Skip invalid JSON data
        
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get existing subtasks for this task
        if self.object and self.object.has_subtasks:
            content_type = ContentType.objects.get_for_model(self.object)
            subtasks = SubTask.objects.filter(
                content_type=content_type,
                object_id=self.object.id
            )
            context['subtasks'] = subtasks
        
        context['is_update'] = True
        return context
    
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
