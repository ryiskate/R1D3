from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages

from .task_models import GameDevelopmentTask
from .task_forms import GameDevelopmentSectionTaskForm
from .game_models import GameProject


class GameDevelopmentTaskCreateView(LoginRequiredMixin, CreateView):
    """
    Create a new game development task without requiring a specific game.
    This view allows creating tasks for the game development section of the company.
    """
    model = GameDevelopmentTask
    form_class = GameDevelopmentSectionTaskForm
    template_name = 'projects/game_development_task_form.html'
    login_url = '/'  # Redirect to home if not logged in
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # No game_id is provided, so we don't filter milestones
        return kwargs
    
    def form_valid(self, form):
        # Set the created_by field to the current user
        form.instance.created_by = self.request.user
        # Explicitly set game to None for section tasks
        form.instance.game = None
        form.instance.milestone = None
        messages.success(self.request, f"Game Development Task '{form.instance.title}' created successfully!")
        return super().form_valid(form)
    
    def get_success_url(self):
        # Redirect back to the game tasks dashboard
        return reverse_lazy('games:task_dashboard')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['section_name'] = "Game Development Task"
        context['is_create'] = True
        return context
