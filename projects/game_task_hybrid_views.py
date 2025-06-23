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
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['company_section'] = self.request.GET.get('section', 'game')
        return kwargs

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Limit milestone choices to the current game
        game_id = self.kwargs.get('game_id')
        if game_id:
            form.fields['milestone'].queryset = GameMilestone.objects.filter(game_id=game_id)
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
            return reverse_lazy('games:game_task_dashboard', kwargs={'game_id': self.object.game.id})
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
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['company_section'] = self.request.GET.get('section', 'game')
        return kwargs

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        company_section = self.request.GET.get('section', 'game')
        
        # Initialize form with section-specific fields
        if company_section == 'education':
            form.fields['course_id'].required = True
            form.fields['learning_objective'].required = True
        elif company_section == 'arcade':
            form.fields['machine_id'].required = True
            form.fields['location'].required = True
            
        # Limit milestone choices to the current game if the task has a game
        if self.object.game:
            form.fields['milestone'].queryset = GameMilestone.objects.filter(game=self.object.game)
            form.fields['gdd_section'].queryset = GDDSection.objects.filter(gdd__game=self.object.game)
        else:
            # For tasks without a game, show all milestones and GDD sections
            form.fields['milestone'].queryset = GameMilestone.objects.all()
            form.fields['gdd_section'].queryset = GDDSection.objects.all()
        return form
    
    def form_valid(self, form):
        messages.success(self.request, f"Task '{form.instance.title}' updated successfully!")
        return super().form_valid(form)
    
    def get_success_url(self):
        # If task is associated with a game, redirect to game task dashboard
        if self.object.game:
            return reverse_lazy('games:game_task_dashboard', kwargs={'game_id': self.object.game.id})
        # Otherwise redirect to global task dashboard
        return reverse_lazy('core:global_task_dashboard')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['game'] = self.object.game
        
        # Set appropriate title based on task context
        if self.object.game:
            context['title'] = f'Update Task for {self.object.game.title}'
        else:
            section = self.object.company_section.replace('_', ' ').title() if self.object.company_section else ''
            if section:
                context['title'] = f'Update {section} Task'
            else:
                context['title'] = 'Update Task'
                
        context['submit_text'] = 'Save Changes'
        return context
