"""
Views for handling all tasks across different company sections in the R1D3 system.
"""
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone
from django.http import JsonResponse
import json
from datetime import date, timedelta

from .task_models import R1D3Task, GameDevelopmentTask, EducationTask, SocialMediaTask, ArcadeTask, ThemeParkTask
from .task_forms import R1D3TaskForm


class AllTasksDashboardView(LoginRequiredMixin, ListView):
    """
    Dashboard view for all tasks across different company sections.
    """
    template_name = 'projects/all_tasks_dashboard.html'
    context_object_name = 'tasks'
    # Temporarily disable pagination for debugging
    # paginate_by = 20
    
    def get(self, request, *args, **kwargs):
        print(f"DEBUG - AllTasksDashboardView.get() called")
        print(f"DEBUG - Template being used: {self.template_name}")
        
        # Call the parent get method
        return super().get(request, *args, **kwargs)
    
    def get_queryset(self):
        # Debug print statements to identify the template being used
        print(f"DEBUG - AllTasksDashboardView template_name: {self.template_name}")
        print(f"DEBUG - AllTasksDashboardView class: {self.__class__.__name__}")
        
        # Get tasks from all models
        r1d3_tasks = list(R1D3Task.objects.all())
        print(f"DEBUG - R1D3 tasks: {len(r1d3_tasks)} - {[task.title for task in r1d3_tasks]}")
        print(f"DEBUG - R1D3 task statuses: {[task.status for task in r1d3_tasks]}")
        print(f"DEBUG - R1D3 task types: {[type(task) for task in r1d3_tasks]}")
        print(f"DEBUG - R1D3 task classes: {[task.__class__.__name__ for task in r1d3_tasks]}")
        print(f"DEBUG - R1D3 task models: {[task._meta.model_name for task in r1d3_tasks]}")
        print(f"DEBUG - R1D3 task apps: {[task._meta.app_label for task in r1d3_tasks]}")
        
        
        game_tasks = list(GameDevelopmentTask.objects.all())
        education_tasks = list(EducationTask.objects.all())
        social_media_tasks = list(SocialMediaTask.objects.all())
        arcade_tasks = list(ArcadeTask.objects.all())
        theme_park_tasks = list(ThemeParkTask.objects.all())
        
        # Combine all tasks
        all_tasks = r1d3_tasks + game_tasks + education_tasks + social_media_tasks + arcade_tasks + theme_park_tasks
        print(f"DEBUG - All tasks: {len(all_tasks)}")
        print(f"DEBUG - Task types: {[task.__class__.__name__ for task in all_tasks]}")
        print(f"DEBUG - Task titles: {[task.title for task in all_tasks]}")
        print(f"DEBUG - Task IDs: {[task.id for task in all_tasks]}")
        print(f"DEBUG - First R1D3 task class: {r1d3_tasks[0].__class__.__name__ if r1d3_tasks else 'None'}")
        print(f"DEBUG - First task in all_tasks class: {all_tasks[0].__class__.__name__ if all_tasks else 'None'}")
        
        
        # Apply filters from GET parameters
        status_filter = self.request.GET.get('status')
        priority_filter = self.request.GET.get('priority')
        assigned_filter = self.request.GET.get('assigned_to')
        
        # Filter tasks based on parameters
        if status_filter:
            all_tasks = [task for task in all_tasks if task.status == status_filter]
        if priority_filter:
            all_tasks = [task for task in all_tasks if task.priority == priority_filter]
        if assigned_filter:
            all_tasks = [task for task in all_tasks if task.assigned_to and str(task.assigned_to.id) == assigned_filter]
            
        # Sort tasks by priority and due date
        all_tasks.sort(key=lambda x: (
            # Sort by priority (critical > high > medium > low)
            {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}.get(x.priority, 4),
            # Then by due date (None at the end)
            x.due_date if x.due_date else date(2099, 12, 31)
        ))
        
        return all_tasks
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add template identification information
        context['template_name'] = self.template_name
        context['view_class'] = self.__class__.__name__
        
        # Get today's date for overdue highlighting
        context['today'] = date.today()
        
        # Get task counts by status
        all_tasks = self.get_queryset()
        
        # Debug output for tasks in context
        print(f"DEBUG - Context tasks: {len(context['tasks'])}")
        print(f"DEBUG - Context task types: {[task.__class__.__name__ for task in context['tasks']]}")
        print(f"DEBUG - Context task titles: {[task.title for task in context['tasks']]}")
        
        # Count tasks by status
        tasks_by_status = {
            'todo': {'count': 0, 'percentage': 0},
            'in_progress': {'count': 0, 'percentage': 0},
            'done': {'count': 0, 'percentage': 0},
            'blocked': {'count': 0, 'percentage': 0},
        }
        
        # Count tasks by priority
        tasks_by_priority = {
            'critical': {'count': 0, 'percentage': 0},
            'high': {'count': 0, 'percentage': 0},
            'medium': {'count': 0, 'percentage': 0},
            'low': {'count': 0, 'percentage': 0},
        }
        
        # Count tasks by status and priority
        for task in self.object_list:
            # Debug each task
            print(f"DEBUG - Processing task: {task.id} - {task.title} ({task.__class__.__name__}) - Status: {task.status}")
            
            # Handle status mapping (some models might use different status values)
            status_key = task.status
            if status_key not in tasks_by_status:
                print(f"DEBUG - Unknown status: {status_key} for task {task.id}")
                status_key = 'todo'  # Default to todo for unknown statuses
                
            tasks_by_status[status_key]['count'] += 1
            
            # Track priority counts
            priority_key = task.priority
            if priority_key not in tasks_by_priority:
                print(f"DEBUG - Unknown priority: {priority_key} for task {task.id}")
                priority_key = 'medium'  # Default to medium for unknown priorities
                
            tasks_by_priority[priority_key]['count'] += 1
        
        # Calculate percentages
        total_tasks = len(self.object_list)
        if total_tasks > 0:
            for status in tasks_by_status:
                count = tasks_by_status[status]['count']
                tasks_by_status[status] = {
                    'count': count,
                    'percentage': int((count / total_tasks) * 100)
                }
            
            for priority in tasks_by_priority:
                count = tasks_by_priority[priority]['count']
                tasks_by_priority[priority] = {
                    'count': count,
                    'percentage': int((count / total_tasks) * 100)
                }
        
        context['tasks_by_status'] = tasks_by_status
        context['tasks_by_priority'] = tasks_by_priority
        context['total_tasks'] = total_tasks
        context['today'] = date.today()
        
        # Add filter options
        context['status_choices'] = R1D3Task.STATUS_CHOICES
        context['priority_choices'] = R1D3Task.PRIORITY_CHOICES
        
        return context


class AllTasksR1D3CreateView(LoginRequiredMixin, CreateView):
    """
    Create a new R1D3 task from the all-tasks dashboard.
    """
    model = R1D3Task
    form_class = R1D3TaskForm
    template_name = 'projects/r1d3_task_form.html'
    
    def form_valid(self, form):
        # Set the created_by field to the current user
        form.instance.created_by = self.request.user
        messages.success(self.request, f"R1D3 Task '{form.instance.title}' created successfully!")
        return super().form_valid(form)
    
    def get_success_url(self):
        # Redirect to the R1D3 tasks dashboard at /R1D3-tasks/
        return reverse_lazy('core:global_task_dashboard')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['section_name'] = "R1D3 Task"
        context['is_create'] = True
        return context
