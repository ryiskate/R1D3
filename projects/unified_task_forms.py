from django.views.generic import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import get_object_or_404
from datetime import date

from .task_models import (
    GameDevelopmentTask, EducationTask, SocialMediaTask, 
    ArcadeTask, ThemeParkTask, R1D3Task
)
from .task_forms import (
    GameDevelopmentTaskForm, EducationTaskForm, SocialMediaTaskForm,
    ArcadeTaskForm, ThemeParkTaskForm, R1D3TaskForm
)
from .game_models import GameProject
from .base_task_views import BaseTaskCreateView, BaseTaskUpdateView


class UnifiedTaskCreateView(BaseTaskCreateView):
    """
    Base class for unified task creation across all task types
    Subclasses should define:
    - model: The task model to use
    - form_class: The form class to use
    - section_name: The name of the section (for context and messages)
    - success_url_name: The URL name for redirecting after success
    """
    section_name = "Task"
    success_url_name = "projects:task_list"
    
    def form_valid(self, form):
        # Set the created_by field to the current user
        form.instance.created_by = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self):
        messages.success(self.request, f"{self.section_name} '{self.object.title}' created successfully!")
        return reverse_lazy(self.success_url_name)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['section_name'] = self.section_name
        return context


class UnifiedTaskUpdateView(BaseTaskUpdateView):
    """
    Base class for unified task updates across all task types
    Subclasses should define:
    - model: The task model to use
    - form_class: The form class to use
    - section_name: The name of the section (for context and messages)
    - detail_url_name: The URL name for redirecting after success
    """
    section_name = "Task"
    detail_url_name = "projects:task_detail"
    
    def get_success_url(self):
        messages.success(self.request, f"{self.section_name} '{self.object.title}' updated successfully!")
        return reverse_lazy(self.detail_url_name, kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['section_name'] = self.section_name
        return context


# Game Development Task Views
class GameTaskCreateView(UnifiedTaskCreateView):
    """Create a new game development task"""
    model = GameDevelopmentTask
    form_class = GameDevelopmentTaskForm
    section_name = "Game Development Task"
    success_url_name = "projects:game_task_dashboard"
    template_name = "projects/game_task_form.html"
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Add game_id to form kwargs for filtering related fields
        kwargs['game_id'] = self.kwargs.get('game_id')
        return kwargs
    
    def form_valid(self, form):
        # Set the game for the task
        form.instance.game_id = self.kwargs.get('game_id')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        game_id = self.kwargs.get('game_id')
        context['game'] = get_object_or_404(GameProject, id=game_id)
        return context


class GameTaskUpdateView(UnifiedTaskUpdateView):
    """Update an existing game development task"""
    model = GameDevelopmentTask
    form_class = GameDevelopmentTaskForm
    section_name = "Game Development Task"
    detail_url_name = "projects:game_task_detail"
    template_name = "projects/game_task_form.html"
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Add game_id to form kwargs for filtering related fields if game exists
        if hasattr(self.object, 'game') and self.object.game:
            kwargs['game_id'] = self.object.game.id
        else:
            # If no game is associated, set game_id to None
            kwargs['game_id'] = None
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Safely add the game to context if it exists
        if hasattr(self.object, 'game') and self.object.game:
            context['game'] = self.object.game
        else:
            context['game'] = None
        return context


# Education Task Views
class EducationTaskCreateView(UnifiedTaskCreateView):
    """Create a new education task"""
    model = EducationTask
    form_class = EducationTaskForm
    section_name = "Education Task"
    success_url_name = "projects:education_task_dashboard"
    template_name = "projects/education_task_form.html"


class EducationTaskUpdateView(UnifiedTaskUpdateView):
    """Update an existing education task"""
    model = EducationTask
    form_class = EducationTaskForm
    section_name = "Education Task"
    detail_url_name = "projects:education_task_detail"
    template_name = "projects/education_task_form.html"


# Social Media Task Views
class SocialMediaTaskCreateView(UnifiedTaskCreateView):
    """Create a new social media task"""
    model = SocialMediaTask
    form_class = SocialMediaTaskForm
    section_name = "Social Media Task"
    success_url_name = "projects:social_media_task_dashboard"
    template_name = "projects/social_media_task_form.html"


class SocialMediaTaskUpdateView(UnifiedTaskUpdateView):
    """Update an existing social media task"""
    model = SocialMediaTask
    form_class = SocialMediaTaskForm
    section_name = "Social Media Task"
    detail_url_name = "projects:social_media_task_detail"
    template_name = "projects/social_media_task_form.html"


# Arcade Task Views
class ArcadeTaskCreateView(UnifiedTaskCreateView):
    """Create a new arcade task"""
    model = ArcadeTask
    form_class = ArcadeTaskForm
    section_name = "Arcade Task"
    success_url_name = "projects:arcade_task_dashboard"
    template_name = "arcade/task_form.html"


class ArcadeTaskUpdateView(UnifiedTaskUpdateView):
    """Update an existing arcade task"""
    model = ArcadeTask
    form_class = ArcadeTaskForm
    section_name = "Arcade Task"
    detail_url_name = "projects:arcade_task_detail"
    template_name = "arcade/task_form.html"


# Theme Park Task Views
class ThemeParkTaskCreateView(UnifiedTaskCreateView):
    """Create a new theme park task"""
    model = ThemeParkTask
    form_class = ThemeParkTaskForm
    section_name = "Theme Park Task"
    success_url_name = "projects:theme_park_task_dashboard"
    template_name = "theme_park/task_form.html"


class ThemeParkTaskUpdateView(UnifiedTaskUpdateView):
    """Update an existing theme park task"""
    model = ThemeParkTask
    form_class = ThemeParkTaskForm
    section_name = "Theme Park Task"
    detail_url_name = "projects:theme_park_task_detail"
    template_name = "theme_park/task_form.html"


# R1D3 General Task Views
class R1D3TaskCreateView(UnifiedTaskCreateView):
    """Create a new R1D3 general task"""
    model = R1D3Task
    form_class = R1D3TaskForm
    section_name = "R1D3 Task"
    success_url_name = "projects:r1d3_task_dashboard"
    template_name = "projects/r1d3_task_form.html"


class R1D3TaskUpdateView(UnifiedTaskUpdateView):
    """Update an existing R1D3 general task"""
    model = R1D3Task
    form_class = R1D3TaskForm
    section_name = "R1D3 Task"
    detail_url_name = "projects:r1d3_task_detail"
    template_name = "projects/r1d3_task_form.html"
