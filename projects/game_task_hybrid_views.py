import json
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.db.models import Q, Sum, Count
from django.utils import timezone
from datetime import date

from .game_models import (
    GameProject, GameDesignDocument, GameAsset, GameMilestone, 
    GameTask, GDDSection
)
from .game_forms import GameTaskForm


class GameTaskHybridDetailView(LoginRequiredMixin, DetailView):
    """
    View details of a specific task with section-specific fields based on company section
    """
    model = GameTask
    template_name = 'projects/task_detail_hybrid.html'
    context_object_name = 'task'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['game'] = self.object.game
        context['today'] = date.today()
        return context


class GameTaskHybridCreateView(LoginRequiredMixin, CreateView):
    """
    Create a new task for a game with section-specific fields based on company section
    """
    model = GameTask
    form_class = GameTaskForm
    template_name = 'projects/task_form_hybrid.html'
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Limit milestone choices to the current game
        game_id = self.kwargs.get('game_id')
        if game_id:
            form.fields['milestone'].queryset = GameMilestone.objects.filter(game_id=game_id)
            form.fields['gdd_section'].queryset = GDDSection.objects.filter(gdd__game_id=game_id)
            
            # Get section from query parameter or default to game_development for game context
            section = self.request.GET.get('section', 'game_development')
            form.fields['company_section'].initial = section
            
            # If section is explicitly set to game_development, make the game field required
            if section == 'game_development':
                form.fields['game'].required = True
        else:
            # For global task creation, show all milestones and GDD sections
            form.fields['milestone'].queryset = GameMilestone.objects.all()
            form.fields['gdd_section'].queryset = GDDSection.objects.all()
            
            # Pre-select company section from query parameter if provided
            section = self.request.GET.get('section', 'r1d3')
            form.fields['company_section'].initial = section
            
            # For R1D3 tasks, the game field should not be required
            if section == 'r1d3':
                form.fields['game'].required = False
        return form
    
    def form_valid(self, form):
        # Set the game for this task if provided
        game_id = self.kwargs.get('game_id')
        if game_id:
            form.instance.game_id = game_id
        
        # Set the creator as the current user if not specified
        if not form.instance.assigned_to:
            form.instance.assigned_to = self.request.user
            
        messages.success(self.request, f"Task '{form.instance.title}' created successfully!")
        return super().form_valid(form)
    
    def get_success_url(self):
        # If task is associated with a game, redirect to game task dashboard
        if self.object.game:
            return reverse_lazy('games:task_dashboard', kwargs={'game_id': self.object.game.id})
        # Otherwise redirect to global task dashboard
        return reverse_lazy('core:global_task_dashboard')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        game_id = self.kwargs.get('game_id')
        
        if game_id:
            context['game'] = get_object_or_404(GameProject, id=game_id)
            context['title'] = f'Create New Task for {context["game"].title}'
        else:
            # For global task creation
            section = self.request.GET.get('section', '').replace('_', ' ').title()
            if section:
                context['title'] = f'Create New {section} Task'
            else:
                context['title'] = 'Create New Task'
                
        context['submit_text'] = 'Create Task'
        return context


class GameTaskHybridUpdateView(LoginRequiredMixin, UpdateView):
    """
    Update an existing task with section-specific fields based on company section
    """
    model = GameTask
    form_class = GameTaskForm
    template_name = 'projects/task_form_hybrid.html'
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Limit milestone choices to the current game
        form.fields['milestone'].queryset = GameMilestone.objects.filter(game=self.object.game)
        form.fields['gdd_section'].queryset = GDDSection.objects.filter(gdd__game=self.object.game)
        return form
    
    def form_valid(self, form):
        messages.success(self.request, f"Task '{form.instance.title}' updated successfully!")
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('games:task_detail_hybrid', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['game'] = self.object.game
        context['title'] = 'Update Task'
        context['submit_text'] = 'Save Changes'
        return context
