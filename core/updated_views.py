"""
Updated views for the R1D3 platform that use the task_type parameter to handle tasks from different models.
"""
from django.shortcuts import render, HttpResponse, redirect
from django.views.generic import TemplateView, View, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q, F
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import Http404
from datetime import date, timedelta

# Import model utilities
from .model_utils import get_task_model_map, get_task_type_for_model


class R1D3TaskUpdateView(LoginRequiredMixin, UpdateView):
    """
    Update an existing task from the global task dashboard.
    This view uses the task_type parameter to determine which model to use.
    """
    template_name = 'projects/r1d3_task_form.html'
    login_url = '/'  # Redirect to home if not logged in
    context_object_name = 'task'
    
    def get_object(self, queryset=None):
        task_id = self.kwargs.get('pk')
        task_type = self.kwargs.get('task_type')
        
        # Get the model map from the utility function
        model_map = get_task_model_map()
        
        # Get the appropriate model based on task_type
        model = model_map.get(task_type)
        if not model:
            raise Http404(f"Invalid task type: {task_type}")
        
        try:
            task = model.objects.get(pk=task_id)
            # Set the appropriate form class and template based on task type
            self._set_task_specifics(model.__name__)
            return task
        except model.DoesNotExist:
            raise Http404(f"No {task_type} task found with ID {task_id}")
    
    def _set_task_specifics(self, model_name):
        # Set form class and template based on task type
        if model_name == 'GameDevelopmentTask':
            from projects.forms import GameDevelopmentTaskForm
            self.form_class = GameDevelopmentTaskForm
            self.template_name = 'projects/game_task_form.html'
            self.section_name = 'Game Development Task'
            self.active_department = 'game_dev'
        elif model_name == 'EducationTask':
            from projects.forms import EducationTaskForm
            self.form_class = EducationTaskForm
            self.template_name = 'projects/education_task_form.html'
            self.section_name = 'Education Task'
            self.active_department = 'education'
        elif model_name == 'SocialMediaTask':
            from projects.forms import SocialMediaTaskForm
            self.form_class = SocialMediaTaskForm
            self.template_name = 'projects/social_media_task_form.html'
            self.section_name = 'Social Media Task'
            self.active_department = 'social_media'
        elif model_name == 'ArcadeTask':
            from arcade.forms import ArcadeTaskForm
            self.form_class = ArcadeTaskForm
            self.template_name = 'arcade/task_form.html'
            self.section_name = 'Arcade Task'
            self.active_department = 'arcade'
        elif model_name == 'ThemeParkTask':
            from projects.forms import ThemeParkTaskForm
            self.form_class = ThemeParkTaskForm
            self.template_name = 'projects/theme_park_task_form.html'
            self.section_name = 'Theme Park Task'
            self.active_department = 'theme_park'
        else:  # Default to R1D3Task
            from projects.forms import R1D3TaskForm
            self.form_class = R1D3TaskForm
            self.template_name = 'projects/r1d3_task_form.html'
            self.section_name = 'R1D3 Task'
            self.active_department = 'r1d3'
    
    def form_valid(self, form):
        messages.success(self.request, f"Task '{form.instance.title}' updated successfully!")
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('core:global_task_dashboard')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['section_name'] = getattr(self, 'section_name', 'Task')
        context['active_department'] = getattr(self, 'active_department', 'r1d3')
        context['is_update'] = True
        return context


class R1D3TaskDeleteView(LoginRequiredMixin, DeleteView):
    """
    Delete an existing task from the global task dashboard.
    This view uses the task_type parameter to determine which model to use.
    """
    template_name = 'projects/task_confirm_delete.html'
    login_url = '/'  # Redirect to home if not logged in
    context_object_name = 'task'
    
    def get_object(self, queryset=None):
        task_id = self.kwargs.get('pk')
        task_type = self.kwargs.get('task_type')
        
        # Get the model map from the utility function
        model_map = get_task_model_map()
        
        # Get the appropriate model based on task_type
        model = model_map.get(task_type)
        if not model:
            raise Http404(f"Invalid task type: {task_type}")
        
        try:
            task = model.objects.get(pk=task_id)
            # Set the appropriate template and section name based on task type
            self._set_task_specifics(model.__name__)
            return task
        except model.DoesNotExist:
            raise Http404(f"No {task_type} task found with ID {task_id}")
    
    def _set_task_specifics(self, model_name):
        # Set template and section name based on task type
        if model_name == 'GameDevelopmentTask':
            self.template_name = 'projects/game_task_confirm_delete.html'
            self.section_name = 'Game Development Task'
            self.active_department = 'game_dev'
        elif model_name == 'EducationTask':
            self.template_name = 'projects/education_task_confirm_delete.html'
            self.section_name = 'Education Task'
            self.active_department = 'education'
        elif model_name == 'SocialMediaTask':
            self.template_name = 'projects/social_media_task_confirm_delete.html'
            self.section_name = 'Social Media Task'
            self.active_department = 'social_media'
        elif model_name == 'ArcadeTask':
            self.template_name = 'arcade/task_confirm_delete.html'
            self.section_name = 'Arcade Task'
            self.active_department = 'arcade'
        elif model_name == 'ThemeParkTask':
            self.template_name = 'projects/theme_park_task_confirm_delete.html'
            self.section_name = 'Theme Park Task'
            self.active_department = 'theme_park'
        else:  # Default to R1D3Task
            self.template_name = 'projects/task_confirm_delete.html'
            self.section_name = 'R1D3 Task'
            self.active_department = 'r1d3'
    
    def get_success_url(self):
        messages.success(self.request, f"Task '{self.object.title}' deleted successfully!")
        return reverse_lazy('core:global_task_dashboard')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['section_name'] = getattr(self, 'section_name', 'Task')
        context['active_department'] = getattr(self, 'active_department', 'r1d3')
        return context


class R1D3TaskDetailView(LoginRequiredMixin, DetailView):
    """
    View an existing task from the global task dashboard.
    This view uses the task_type parameter to determine which model to use.
    """
    template_name = 'projects/r1d3_task_detail.html'
    login_url = '/'  # Redirect to home if not logged in
    context_object_name = 'task'
    
    def get_object(self, queryset=None):
        task_id = self.kwargs.get('pk')
        task_type = self.kwargs.get('task_type')
        
        # Get the model map from the utility function
        model_map = get_task_model_map()
        
        # Get the appropriate model based on task_type
        model = model_map.get(task_type)
        if not model:
            raise Http404(f"Invalid task type: {task_type}")
        
        try:
            task = model.objects.get(pk=task_id)
            # Set the appropriate template and section name based on task type
            self._set_task_specifics(model.__name__)
            return task
        except model.DoesNotExist:
            raise Http404(f"No {task_type} task found with ID {task_id}")
    
    def _set_task_specifics(self, model_name):
        # Set template and section name based on task type
        if model_name == 'GameDevelopmentTask':
            self.template_name = 'projects/game_task_detail.html'
            self.section_name = 'Game Development Task'
            self.active_department = 'game_dev'
        elif model_name == 'EducationTask':
            self.template_name = 'projects/education_task_detail.html'
            self.section_name = 'Education Task'
            self.active_department = 'education'
        elif model_name == 'SocialMediaTask':
            self.template_name = 'projects/social_media_task_detail.html'
            self.section_name = 'Social Media Task'
            self.active_department = 'social_media'
        elif model_name == 'ArcadeTask':
            self.template_name = 'arcade/task_detail.html'
            self.section_name = 'Arcade Task'
            self.active_department = 'arcade'
        elif model_name == 'ThemeParkTask':
            self.template_name = 'projects/theme_park_task_detail.html'
            self.section_name = 'Theme Park Task'
            self.active_department = 'theme_park'
        else:  # Default to R1D3Task
            self.template_name = 'projects/r1d3_task_detail.html'
            self.section_name = 'R1D3 Task'
            self.active_department = 'r1d3'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['section_name'] = getattr(self, 'section_name', 'Task')
        context['active_department'] = getattr(self, 'active_department', 'r1d3')
        return context
