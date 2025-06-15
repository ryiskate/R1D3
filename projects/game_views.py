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
    GameTask, GameBuild, PlaytestSession, PlaytestFeedback, GameBug
)
from .game_forms import (GameProjectForm, GameDesignDocumentForm, GameAssetForm,
    GameTaskForm, GameMilestoneForm, GameBuildForm, PlaytestSessionForm,
    PlaytestFeedbackForm, GameBugForm
)


class GameDashboardView(LoginRequiredMixin, ListView):
    """
    Dashboard view for game development projects
    """
    model = GameProject
    template_name = 'projects/game_dashboard.html'
    context_object_name = 'games'
    
    def get_queryset(self):
        # Show active game projects by default
        return GameProject.objects.filter(status__in=['pre_production', 'production', 'alpha', 'beta'])
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_games'] = GameProject.objects.count()
        context['active_games'] = GameProject.objects.filter(
            status__in=['pre_production', 'production', 'alpha', 'beta']
        ).count()
        context['released_games'] = GameProject.objects.filter(
            status__in=['release', 'post_release']
        ).count()
        context['my_tasks'] = GameTask.objects.filter(
            assigned_to=self.request.user, 
            status__in=['backlog', 'to_do', 'in_progress', 'in_review', 'blocked']
        )
        context['overdue_tasks'] = GameTask.objects.filter(
            due_date__lt=timezone.now().date(),
            status__in=['to_do', 'in_progress']
        )
        context['recent_builds'] = GameBuild.objects.order_by('-build_date')[:5]
        return context


class GameTaskDetailView(LoginRequiredMixin, DetailView):
    """
    View details of a specific task
    """
    model = GameTask
    template_name = 'projects/task_detail.html'
    context_object_name = 'task'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['game'] = self.object.game
        context['today'] = date.today()
        return context


class GameTaskCreateView(LoginRequiredMixin, CreateView):
    """
    Create a new task for a game
    """
    model = GameTask
    form_class = GameTaskForm
    template_name = 'projects/task_form.html'
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Limit milestone choices to the current game
        game_id = self.kwargs.get('game_id')
        if game_id:
            form.fields['milestone'].queryset = GameMilestone.objects.filter(game_id=game_id)
        return form
    
    def form_valid(self, form):
        # Set the game for this task
        game_id = self.kwargs.get('game_id')
        form.instance.game_id = game_id
        
        # Set the creator as the current user if not specified
        if not form.instance.assigned_to:
            form.instance.assigned_to = self.request.user
            
        messages.success(self.request, f"Task '{form.instance.title}' created successfully!")
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('games:task_list', kwargs={'game_id': self.object.game.id})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        game_id = self.kwargs.get('game_id')
        context['game'] = get_object_or_404(GameProject, id=game_id)
        context['title'] = 'Create New Task'
        context['submit_text'] = 'Create Task'
        return context


class GameTaskUpdateView(LoginRequiredMixin, UpdateView):
    """
    Update an existing task
    """
    model = GameTask
    form_class = GameTaskForm
    template_name = 'projects/task_form.html'
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Limit milestone choices to the current game
        form.fields['milestone'].queryset = GameMilestone.objects.filter(game=self.object.game)
        return form
    
    def form_valid(self, form):
        messages.success(self.request, f"Task '{form.instance.title}' updated successfully!")
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('games:task_detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['game'] = self.object.game
        context['title'] = 'Update Task'
        context['submit_text'] = 'Save Changes'
        return context


class GameTaskDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Delete a task
    """
    model = GameTask
    template_name = 'projects/task_confirm_delete.html'
    context_object_name = 'task'
    
    def test_func(self):
        # Only allow task deletion by staff or the task creator
        return self.request.user.is_staff or self.get_object().assigned_to == self.request.user
    
    def get_success_url(self):
        messages.success(self.request, f"Task '{self.object.title}' deleted successfully!")
        return reverse_lazy('games:task_list', kwargs={'game_id': self.object.game.id})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['game'] = self.object.game
        context['today'] = date.today()
        return context


class GameTaskKanbanView(LoginRequiredMixin, ListView):
    """
    Kanban board view for tasks
    """
    model = GameTask
    template_name = 'projects/task_kanban.html'
    context_object_name = 'tasks'
    
    def get_queryset(self):
        queryset = GameTask.objects.all()
        
        # Filter by game if provided
        game_id = self.kwargs.get('game_id')
        if game_id:
            queryset = queryset.filter(game_id=game_id)
            
        # Filter by assigned user if requested
        if self.request.GET.get('my_tasks'):
            queryset = queryset.filter(assigned_to=self.request.user)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add game to context if filtering by game
        game_id = self.kwargs.get('game_id')
        if game_id:
            context['game'] = get_object_or_404(GameProject, id=game_id)
        
        # Group tasks by status for kanban columns
        tasks_by_status = {}
        for status, label in GameTask.STATUS_CHOICES:
            tasks_by_status[status] = self.get_queryset().filter(status=status).order_by('-priority', 'due_date')
        
        context['tasks_by_status'] = tasks_by_status
        context['status_choices'] = GameTask.STATUS_CHOICES
        context['today'] = date.today()
        
        return context

class GameProjectListView(LoginRequiredMixin, ListView):
    """
    List all game projects
    """
    model = GameProject
    template_name = 'projects/game_list.html'
    context_object_name = 'games'
    
    def get_queryset(self):
        queryset = GameProject.objects.all()
        
        # Filter by status if provided
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
            
        # Filter by platform if provided
        platform = self.request.GET.get('platform')
        if platform:
            queryset = queryset.filter(platforms=platform)
            
        # Filter by genre if provided
        genre = self.request.GET.get('genre')
        if genre:
            queryset = queryset.filter(genre=genre)
            
        # Filter by search query if provided
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) | 
                Q(description__icontains=query) |
                Q(tagline__icontains=query)
            )
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add user's tasks to the context - simplified approach
        if self.request.user.is_authenticated:
            # Get all tasks assigned to the user
            user_tasks = GameTask.objects.filter(assigned_to=self.request.user)
            
            # Add to context
            context['my_tasks'] = user_tasks
            context['task_count'] = user_tasks.count()
            
            # Also add task counts by status for debugging
            context['task_counts_by_status'] = {
                'backlog': user_tasks.filter(status='backlog').count(),
                'to_do': user_tasks.filter(status='to_do').count(),
                'in_progress': user_tasks.filter(status='in_progress').count(),
                'in_review': user_tasks.filter(status='in_review').count(),
                'done': user_tasks.filter(status='done').count(),
                'blocked': user_tasks.filter(status='blocked').count(),
            }
        
        return context


class GameProjectDetailView(LoginRequiredMixin, DetailView):
    """
    View details of a specific game project
    """
    model = GameProject
    template_name = 'projects/game_detail.html'
    context_object_name = 'game'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        game = self.object
        
        # Get game design document
        try:
            context['gdd'] = game.design_document
        except GameDesignDocument.DoesNotExist:
            context['gdd'] = None
        
        # Get game milestones
        context['milestones'] = game.milestones.all().order_by('due_date')
        
        # Get game tasks
        context['tasks'] = game.tasks.all().order_by('-priority', 'due_date')
        context['tasks_by_status'] = {
            'backlog': game.tasks.filter(status='backlog').count(),
            'to_do': game.tasks.filter(status='to_do').count(),
            'in_progress': game.tasks.filter(status='in_progress').count(),
            'in_review': game.tasks.filter(status='in_review').count(),
            'done': game.tasks.filter(status='done').count(),
            'blocked': game.tasks.filter(status='blocked').count(),
        }
        
        # Get game assets
        context['assets'] = game.assets.all()
        context['assets_by_type'] = {
            '3d_model': game.assets.filter(asset_type='3d_model').count(),
            '2d_image': game.assets.filter(asset_type='2d_image').count(),
            'music': game.assets.filter(asset_type='music').count(),
            'video': game.assets.filter(asset_type='video').count(),
            'reference': game.assets.filter(asset_type='reference').count(),
            'other': game.assets.filter(asset_type='other').count(),
        }
        
        # Get game builds
        context['builds'] = game.builds.all().order_by('-build_date')
        
        # Get bugs
        context['bugs'] = game.bugs.all().order_by('-severity')
        context['open_bugs'] = game.bugs.filter(status__in=['open', 'confirmed', 'in_progress']).count()
        
        # Add status choices for the status change dropdown
        context['status_choices'] = GameProject.STATUS_CHOICES
        
        return context


class GameTaskDetailView(LoginRequiredMixin, DetailView):
    """
    View details of a specific task
    """
    model = GameTask
    template_name = 'projects/task_detail.html'
    context_object_name = 'task'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['game'] = self.object.game
        context['today'] = date.today()
        return context


class GameTaskCreateView(LoginRequiredMixin, CreateView):
    """
    Create a new task for a game
    """
    model = GameTask
    form_class = GameTaskForm
    template_name = 'projects/task_form.html'
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Limit milestone choices to the current game
        game_id = self.kwargs.get('game_id')
        if game_id:
            form.fields['milestone'].queryset = GameMilestone.objects.filter(game_id=game_id)
        return form
    
    def form_valid(self, form):
        # Set the game for this task
        game_id = self.kwargs.get('game_id')
        form.instance.game_id = game_id
        
        # Set the creator as the current user if not specified
        if not form.instance.assigned_to:
            form.instance.assigned_to = self.request.user
            
        messages.success(self.request, f"Task '{form.instance.title}' created successfully!")
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('games:task_list', kwargs={'game_id': self.object.game.id})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        game_id = self.kwargs.get('game_id')
        context['game'] = get_object_or_404(GameProject, id=game_id)
        context['title'] = 'Create New Task'
        context['submit_text'] = 'Create Task'
        return context


class GameTaskUpdateView(LoginRequiredMixin, UpdateView):
    """
    Update an existing task
    """
    model = GameTask
    form_class = GameTaskForm
    template_name = 'projects/task_form.html'
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Limit milestone choices to the current game
        form.fields['milestone'].queryset = GameMilestone.objects.filter(game=self.object.game)
        return form
    
    def form_valid(self, form):
        messages.success(self.request, f"Task '{form.instance.title}' updated successfully!")
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('games:task_detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['game'] = self.object.game
        context['title'] = 'Update Task'
        context['submit_text'] = 'Save Changes'
        return context


class GameTaskDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Delete a task
    """
    model = GameTask
    template_name = 'projects/task_confirm_delete.html'
    context_object_name = 'task'
    
    def test_func(self):
        # Only allow task deletion by staff or the task creator
        return self.request.user.is_staff or self.get_object().assigned_to == self.request.user
    
    def get_success_url(self):
        messages.success(self.request, f"Task '{self.object.title}' deleted successfully!")
        return reverse_lazy('games:task_list', kwargs={'game_id': self.object.game.id})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['game'] = self.object.game
        context['today'] = date.today()
        return context


class GameTaskKanbanView(LoginRequiredMixin, ListView):
    """
    Kanban board view for tasks
    """
    model = GameTask
    template_name = 'projects/task_kanban.html'
    context_object_name = 'tasks'
    
    def get_queryset(self):
        queryset = GameTask.objects.all()
        
        # Filter by game if provided
        game_id = self.kwargs.get('game_id')
        if game_id:
            queryset = queryset.filter(game_id=game_id)
            
        # Filter by assigned user if requested
        if self.request.GET.get('my_tasks'):
            queryset = queryset.filter(assigned_to=self.request.user)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add game to context if filtering by game
        game_id = self.kwargs.get('game_id')
        if game_id:
            context['game'] = get_object_or_404(GameProject, id=game_id)
        
        # Group tasks by status for kanban columns
        tasks_by_status = {}
        for status, label in GameTask.STATUS_CHOICES:
            tasks_by_status[status] = self.get_queryset().filter(status=status).order_by('-priority', 'due_date')
        
        context['tasks_by_status'] = tasks_by_status
        context['status_choices'] = GameTask.STATUS_CHOICES
        context['today'] = date.today()
        
        return context

class GameProjectCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """
    Create a new game project with GitHub integration
    """
    model = GameProject
    form_class = GameProjectForm
    template_name = 'projects/game_form.html'
    success_url = reverse_lazy('games:dashboard')
    
    def test_func(self):
        # Only staff members can create projects
        return self.request.user.is_staff
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create New Game Project'
        context['submit_text'] = 'Create Project'
        context['show_github_section'] = True
        return context


class GameProjectUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Update an existing game project
    """
    model = GameProject
    form_class = GameProjectForm
    template_name = 'projects/game_form.html'
    
    def test_func(self):
        # Only staff members can edit projects
        return self.request.user.is_staff
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Edit Game Project: {self.object.title}'
        context['submit_text'] = 'Update Project'
        context['show_github_section'] = True
        return context
    
    def form_valid(self, form):
        # Handle GitHub integration updates if needed
        if form.cleaned_data.get('github_repository'):
            # Update GitHub token securely if changed
            pass
            
        messages.success(self.request, f"Game project '{form.instance.title}' updated successfully!")
        return super().form_valid(form)
    
    def get_success_url(self):
        # Redirect to the updated game's detail page
        return reverse_lazy('games:game_detail', kwargs={'pk': self.object.pk})


class GameTaskDetailView(LoginRequiredMixin, DetailView):
    """
    View details of a specific task
    """
    model = GameTask
    template_name = 'projects/task_detail.html'
    context_object_name = 'task'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['game'] = self.object.game
        context['today'] = date.today()
        return context


class GameTaskCreateView(LoginRequiredMixin, CreateView):
    """
    Create a new task for a game
    """
    model = GameTask
    form_class = GameTaskForm
    template_name = 'projects/task_form.html'
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Limit milestone choices to the current game
        game_id = self.kwargs.get('game_id')
        if game_id:
            form.fields['milestone'].queryset = GameMilestone.objects.filter(game_id=game_id)
        return form
    
    def form_valid(self, form):
        # Set the game for this task
        game_id = self.kwargs.get('game_id')
        form.instance.game_id = game_id
        
        # Set the creator as the current user if not specified
        if not form.instance.assigned_to:
            form.instance.assigned_to = self.request.user
            
        messages.success(self.request, f"Task '{form.instance.title}' created successfully!")
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('games:task_list', kwargs={'game_id': self.object.game.id})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        game_id = self.kwargs.get('game_id')
        context['game'] = get_object_or_404(GameProject, id=game_id)
        context['title'] = 'Create New Task'
        context['submit_text'] = 'Create Task'
        return context


class GameTaskUpdateView(LoginRequiredMixin, UpdateView):
    """
    Update an existing task
    """
    model = GameTask
    form_class = GameTaskForm
    template_name = 'projects/task_form.html'
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Limit milestone choices to the current game
        form.fields['milestone'].queryset = GameMilestone.objects.filter(game=self.object.game)
        return form
    
    def form_valid(self, form):
        messages.success(self.request, f"Task '{form.instance.title}' updated successfully!")
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('games:task_detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['game'] = self.object.game
        context['title'] = 'Update Task'
        context['submit_text'] = 'Save Changes'
        return context


class GameTaskDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Delete a task
    """
    model = GameTask
    template_name = 'projects/task_confirm_delete.html'
    context_object_name = 'task'
    
    def test_func(self):
        # Only allow task deletion by staff or the task creator
        return self.request.user.is_staff or self.get_object().assigned_to == self.request.user
    
    def get_success_url(self):
        messages.success(self.request, f"Task '{self.object.title}' deleted successfully!")
        return reverse_lazy('games:task_list', kwargs={'game_id': self.object.game.id})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['game'] = self.object.game
        context['today'] = date.today()
        return context


class GameTaskKanbanView(LoginRequiredMixin, ListView):
    """
    Kanban board view for tasks
    """
    model = GameTask
    template_name = 'projects/task_kanban.html'
    context_object_name = 'tasks'
    
    def get_queryset(self):
        queryset = GameTask.objects.all()
        
        # Filter by game if provided
        game_id = self.kwargs.get('game_id')
        if game_id:
            queryset = queryset.filter(game_id=game_id)
            
        # Filter by assigned user if requested
        if self.request.GET.get('my_tasks'):
            queryset = queryset.filter(assigned_to=self.request.user)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add game to context if filtering by game
        game_id = self.kwargs.get('game_id')
        if game_id:
            context['game'] = get_object_or_404(GameProject, id=game_id)
        
        # Group tasks by status for kanban columns
        tasks_by_status = {}
        for status, label in GameTask.STATUS_CHOICES:
            tasks_by_status[status] = self.get_queryset().filter(status=status).order_by('-priority', 'due_date')
        
        context['tasks_by_status'] = tasks_by_status
        context['status_choices'] = GameTask.STATUS_CHOICES
        context['today'] = date.today()
        
        return context    
    def form_valid(self, form):
        # Set the project lead to the current user if not specified
        if not form.instance.lead_developer:
            form.instance.lead_developer = self.request.user
            
        # Handle GitHub integration
        if form.cleaned_data.get('github_repository'):
            # Store GitHub token securely - in a real app, you'd encrypt this
            # This is just a placeholder for demonstration
            pass
            
        messages.success(self.request, f"Game project '{form.instance.title}' created successfully!")
        return super().form_valid(form)
    
    def get_success_url(self):
        # Redirect to the newly created game's detail page
        return reverse_lazy('games:game_detail', kwargs={'pk': self.object.pk})


class GameDesignDocumentView(LoginRequiredMixin, DetailView):
    """
    View a game design document with support for HTML content and task integration
    """
    model = GameDesignDocument
    template_name = 'projects/gdd_detail_simple.html'
    context_object_name = 'gdd'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['game'] = self.object.game
        
        # Check permissions
        user = self.request.user
        game = self.object.game
        context['can_edit'] = user.is_staff or user == game.lead_developer or user == game.lead_designer
        context['can_create_task'] = user.is_staff or user == game.lead_developer or user == game.lead_designer
        context['can_link_tasks'] = user.is_staff or user == game.lead_developer or user == game.lead_designer
        
        # Get sections and their tasks
        sections_with_tasks = {}
        for section in self.object.sections.all():
            sections_with_tasks[section.id] = list(section.tasks.all())
        
        context['sections_with_tasks'] = sections_with_tasks
        
        # Get unlinked tasks
        all_game_tasks = GameTask.objects.filter(game=game)
        linked_task_ids = []
        for tasks in sections_with_tasks.values():
            linked_task_ids.extend([task.id for task in tasks])
        
        context['unlinked_tasks'] = all_game_tasks.exclude(id__in=linked_task_ids)
        
        # Prepare JSON data for JavaScript
        sections_json = [{
            'id': section.id,
            'title': section.title,
            'section_id': section.section_id
        } for section in self.object.sections.all()]
        context['sections_json'] = json.dumps(sections_json)
        
        sections_with_tasks_json = {}
        for section_id, tasks in sections_with_tasks.items():
            sections_with_tasks_json[section_id] = [{
                'id': task.id,
                'title': task.title,
                'status_display': task.get_status_display()
            } for task in tasks]
        
        context['sections_with_tasks_json'] = json.dumps(sections_with_tasks_json)
        
        # Return the context
        return context


class GameTaskDetailView(LoginRequiredMixin, DetailView):
    """
    View details of a specific task
    """
    model = GameTask
    template_name = 'projects/task_detail.html'
    context_object_name = 'task'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['game'] = self.object.game
        context['today'] = date.today()
        return context


class GameTaskCreateView(LoginRequiredMixin, CreateView):
    """
    Create a new task for a game
    """
    model = GameTask
    form_class = GameTaskForm
    template_name = 'projects/task_form.html'
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Limit milestone choices to the current game
        game_id = self.kwargs.get('game_id')
        if game_id:
            form.fields['milestone'].queryset = GameMilestone.objects.filter(game_id=game_id)
        return form
    
    def form_valid(self, form):
        # Set the game for this task
        game_id = self.kwargs.get('game_id')
        form.instance.game_id = game_id
        
        # Set the creator as the current user if not specified
        if not form.instance.assigned_to:
            form.instance.assigned_to = self.request.user
            
        messages.success(self.request, f"Task '{form.instance.title}' created successfully!")
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('games:task_list', kwargs={'game_id': self.object.game.id})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        game_id = self.kwargs.get('game_id')
        context['game'] = get_object_or_404(GameProject, id=game_id)
        context['title'] = 'Create New Task'
        context['submit_text'] = 'Create Task'
        return context


class GameTaskUpdateView(LoginRequiredMixin, UpdateView):
    """
    Update an existing task
    """
    model = GameTask
    form_class = GameTaskForm
    template_name = 'projects/task_form.html'
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Limit milestone choices to the current game
        form.fields['milestone'].queryset = GameMilestone.objects.filter(game=self.object.game)
        return form
    
    def form_valid(self, form):
        messages.success(self.request, f"Task '{form.instance.title}' updated successfully!")
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('games:task_detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['game'] = self.object.game
        context['title'] = 'Update Task'
        context['submit_text'] = 'Save Changes'
        return context


class GameTaskDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Delete a task
    """
    model = GameTask
    template_name = 'projects/task_confirm_delete.html'
    context_object_name = 'task'
    
    def test_func(self):
        # Only allow task deletion by staff or the task creator
        return self.request.user.is_staff or self.get_object().assigned_to == self.request.user
    
    def get_success_url(self):
        messages.success(self.request, f"Task '{self.object.title}' deleted successfully!")
        return reverse_lazy('games:task_list', kwargs={'game_id': self.object.game.id})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['game'] = self.object.game
        context['today'] = date.today()
        return context


class GameTaskKanbanView(LoginRequiredMixin, ListView):
    """
    Kanban board view for tasks
    """
    model = GameTask
    template_name = 'projects/task_kanban.html'
    context_object_name = 'tasks'
    
    def get_queryset(self):
        queryset = GameTask.objects.all()
        
        # Filter by game if provided
        game_id = self.kwargs.get('game_id')
        if game_id:
            queryset = queryset.filter(game_id=game_id)
            
        # Filter by assigned user if requested
        if self.request.GET.get('my_tasks'):
            queryset = queryset.filter(assigned_to=self.request.user)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add game to context if filtering by game
        game_id = self.kwargs.get('game_id')
        if game_id:
            context['game'] = get_object_or_404(GameProject, id=game_id)
        
        # Group tasks by status for kanban columns
        tasks_by_status = {}
        for status, label in GameTask.STATUS_CHOICES:
            tasks_by_status[status] = self.get_queryset().filter(status=status).order_by('-priority', 'due_date')
        
        context['tasks_by_status'] = tasks_by_status
        context['status_choices'] = GameTask.STATUS_CHOICES
        context['today'] = date.today()
        
        return context

class GameDesignDocumentCreateView(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    Create a game design document or redirect to edit if one already exists
    """
    def test_func(self):
        # Only allow staff or game leads to create GDDs
        game_id = self.kwargs.get('game_id')
        game = get_object_or_404(GameProject, id=game_id)
        return self.request.user.is_staff or self.request.user == game.lead_developer or self.request.user == game.lead_designer
    
    def get(self, request, *args, **kwargs):
        game_id = self.kwargs.get('game_id')
        game = get_object_or_404(GameProject, id=game_id)
        
        # Check if a GDD already exists for this game
        try:
            existing_gdd = GameDesignDocument.objects.get(game=game)
            messages.info(request, "A Game Design Document already exists for this game. You can edit it below.")
            return redirect('games:gdd_edit', pk=existing_gdd.id)
        except GameDesignDocument.DoesNotExist:
            # No GDD exists, proceed to create form
            form = GameDesignDocumentForm()
            return render(request, 'projects/gdd_form.html', {
                'form': form,
                'game': game,
                'game_id': game_id
            })
    
    def post(self, request, *args, **kwargs):
        game_id = self.kwargs.get('game_id')
        game = get_object_or_404(GameProject, id=game_id)
        
        # Check if a GDD already exists for this game
        try:
            existing_gdd = GameDesignDocument.objects.get(game=game)
            messages.error(request, "A Game Design Document already exists for this game. You cannot create another one.")
            return redirect('games:gdd_edit', pk=existing_gdd.id)
        except GameDesignDocument.DoesNotExist:
            # No GDD exists, proceed to create
            form = GameDesignDocumentForm(request.POST)
            if form.is_valid():
                gdd = form.save(commit=False)
                gdd.game = game
                gdd.save()
                messages.success(request, "Game Design Document created successfully!")
                return redirect('games:game_detail', pk=game.id)
            else:
                return render(request, 'projects/gdd_form.html', {
                    'form': form,
                    'game': game,
                    'game_id': game_id
                })


class GameAssetListView(LoginRequiredMixin, ListView):
    """
    List assets for a game with filtering and sorting options
    """
    model = GameAsset
    template_name = 'projects/asset_list.html'
    context_object_name = 'assets'
    paginate_by = 12
    
    def get_queryset(self):
        game_id = self.kwargs.get('game_id')
        queryset = GameAsset.objects.filter(game_id=game_id)
        
        # Apply filters
        type_filter = self.request.GET.get('type')
        status_filter = self.request.GET.get('status')
        search_query = self.request.GET.get('search')
        sort_by = self.request.GET.get('sort')
        
        if type_filter:
            queryset = queryset.filter(asset_type=type_filter)
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        if search_query:
            queryset = queryset.filter(
                models.Q(name__icontains=search_query) |
                models.Q(description__icontains=search_query) |
                models.Q(subtype__icontains=search_query) |
                models.Q(tags__icontains=search_query)
            )
        
        # Apply sorting
        if sort_by == 'name':
            queryset = queryset.order_by('name')
        elif sort_by == 'type':
            queryset = queryset.order_by('asset_type', 'name')
        elif sort_by == 'status':
            queryset = queryset.order_by('status', 'name')
        elif sort_by == 'date':
            queryset = queryset.order_by('-created_at')
        else:
            queryset = queryset.order_by('-created_at')  # Default sort
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        game_id = self.kwargs.get('game_id')
        context['game'] = get_object_or_404(GameProject, id=game_id)
        
        # Pass filter parameters to context
        context['type_filter'] = self.request.GET.get('type')
        context['status_filter'] = self.request.GET.get('status')
        context['search_query'] = self.request.GET.get('search')
        context['sort_by'] = self.request.GET.get('sort', 'date')
        
        return context


class GameAssetCreateView(LoginRequiredMixin, CreateView):
    """
    Create a new asset for a game
    """
    model = GameAsset
    form_class = GameAssetForm
    template_name = 'projects/asset_form.html'
    
    def get_success_url(self):
        return reverse('games:asset_list', kwargs={'game_id': self.object.game.id})
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # If you need to customize the form, do it here
        return kwargs
    
    def form_valid(self, form):
        form.instance.game_id = self.kwargs.get('game_id')
        form.instance.created_by = self.request.user
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        game_id = self.kwargs.get('game_id')
        context['game'] = get_object_or_404(GameProject, id=game_id)
        return context


class GameAssetUpdateView(LoginRequiredMixin, UpdateView):
    """
    Update an existing game asset
    """
    model = GameAsset
    form_class = GameAssetForm
    template_name = 'projects/asset_form.html'
    pk_url_kwarg = 'asset_id'
    
    def get_success_url(self):
        return reverse('games:asset_list', kwargs={'game_id': self.object.game.id})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['game'] = self.object.game
        return context


class GameAssetDetailView(LoginRequiredMixin, DetailView):
    """
    View details of a specific asset
    """
    model = GameAsset
    template_name = 'projects/asset_detail.html'
    context_object_name = 'asset'
    pk_url_kwarg = 'asset_id'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['game'] = self.object.game
        return context


class GameTaskDetailView(LoginRequiredMixin, DetailView):
    """
    View details of a specific task
    """
    model = GameTask
    template_name = 'projects/task_detail.html'
    context_object_name = 'task'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['game'] = self.object.game
        context['today'] = date.today()
        return context


class GameTaskCreateView(LoginRequiredMixin, CreateView):
    """
    Create a new task for a game
    """
    model = GameTask
    form_class = GameTaskForm
    template_name = 'projects/task_form.html'
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Limit milestone choices to the current game
        game_id = self.kwargs.get('game_id')
        if game_id:
            form.fields['milestone'].queryset = GameMilestone.objects.filter(game_id=game_id)
        return form
    
    def form_valid(self, form):
        # Set the game for this task
        game_id = self.kwargs.get('game_id')
        form.instance.game_id = game_id
        
        # Set the creator as the current user if not specified
        if not form.instance.assigned_to:
            form.instance.assigned_to = self.request.user
            
        messages.success(self.request, f"Task '{form.instance.title}' created successfully!")
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('games:task_list', kwargs={'game_id': self.object.game.id})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        game_id = self.kwargs.get('game_id')
        context['game'] = get_object_or_404(GameProject, id=game_id)
        context['title'] = 'Create New Task'
        context['submit_text'] = 'Create Task'
        return context


class GameTaskUpdateView(LoginRequiredMixin, UpdateView):
    """
    Update an existing task
    """
    model = GameTask
    form_class = GameTaskForm
    template_name = 'projects/task_form.html'
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Limit milestone choices to the current game
        form.fields['milestone'].queryset = GameMilestone.objects.filter(game=self.object.game)
        return form
    
    def form_valid(self, form):
        messages.success(self.request, f"Task '{form.instance.title}' updated successfully!")
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('games:task_detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['game'] = self.object.game
        context['title'] = 'Update Task'
        context['submit_text'] = 'Save Changes'
        return context


class GameTaskDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Delete a task
    """
    model = GameTask
    template_name = 'projects/task_confirm_delete.html'
    context_object_name = 'task'
    
    def test_func(self):
        # Only allow task deletion by staff or the task creator
        return self.request.user.is_staff or self.get_object().assigned_to == self.request.user
    
    def get_success_url(self):
        messages.success(self.request, f"Task '{self.object.title}' deleted successfully!")
        return reverse_lazy('games:task_list', kwargs={'game_id': self.object.game.id})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['game'] = self.object.game
        context['today'] = date.today()
        return context


class GameTaskKanbanView(LoginRequiredMixin, ListView):
    """
    Kanban board view for tasks
    """
    model = GameTask
    template_name = 'projects/task_kanban.html'
    context_object_name = 'tasks'
    
    def get_queryset(self):
        queryset = GameTask.objects.all()
        
        # Filter by game if provided
        game_id = self.kwargs.get('game_id')
        if game_id:
            queryset = queryset.filter(game_id=game_id)
            
        # Filter by assigned user if requested
        if self.request.GET.get('my_tasks'):
            queryset = queryset.filter(assigned_to=self.request.user)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add game to context if filtering by game
        game_id = self.kwargs.get('game_id')
        if game_id:
            context['game'] = get_object_or_404(GameProject, id=game_id)
        
        # Group tasks by status for kanban columns
        tasks_by_status = {}
        for status, label in GameTask.STATUS_CHOICES:
            tasks_by_status[status] = self.get_queryset().filter(status=status).order_by('-priority', 'due_date')
        
        context['tasks_by_status'] = tasks_by_status
        context['status_choices'] = GameTask.STATUS_CHOICES
        context['today'] = date.today()
        
        return context

class GameAssetCreateView(LoginRequiredMixin, CreateView):
    """
    Create a new game asset
    """
    model = GameAsset
    form_class = GameAssetForm
    template_name = 'projects/asset_form.html'
    
    def form_valid(self, form):
        game_id = self.kwargs.get('game_id')
        form.instance.game = get_object_or_404(GameProject, id=game_id)
        form.instance.created_by = self.request.user
        messages.success(self.request, "Asset created successfully!")
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('games:asset_list', kwargs={'game_id': self.object.game.id})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        game_id = self.kwargs.get('game_id')
        context['game'] = get_object_or_404(GameProject, id=game_id)
        return context


class GameTaskDetailView(LoginRequiredMixin, DetailView):
    """
    View details of a specific task
    """
    model = GameTask
    template_name = 'projects/task_detail.html'
    context_object_name = 'task'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['game'] = self.object.game
        context['today'] = date.today()
        return context


class GameTaskCreateView(LoginRequiredMixin, CreateView):
    """
    Create a new task for a game
    """
    model = GameTask
    form_class = GameTaskForm
    template_name = 'projects/task_form.html'
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Limit milestone choices to the current game
        game_id = self.kwargs.get('game_id')
        if game_id:
            form.fields['milestone'].queryset = GameMilestone.objects.filter(game_id=game_id)
        return form
    
    def form_valid(self, form):
        # Set the game for this task
        game_id = self.kwargs.get('game_id')
        form.instance.game_id = game_id
        
        # Set the creator as the current user if not specified
        if not form.instance.assigned_to:
            form.instance.assigned_to = self.request.user
            
        messages.success(self.request, f"Task '{form.instance.title}' created successfully!")
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('games:task_list', kwargs={'game_id': self.object.game.id})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        game_id = self.kwargs.get('game_id')
        context['game'] = get_object_or_404(GameProject, id=game_id)
        context['title'] = 'Create New Task'
        context['submit_text'] = 'Create Task'
        return context


class GameTaskUpdateView(LoginRequiredMixin, UpdateView):
    """
    Update an existing task
    """
    model = GameTask
    form_class = GameTaskForm
    template_name = 'projects/task_form.html'
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Limit milestone choices to the current game
        form.fields['milestone'].queryset = GameMilestone.objects.filter(game=self.object.game)
        return form
    
    def form_valid(self, form):
        messages.success(self.request, f"Task '{form.instance.title}' updated successfully!")
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('games:task_detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['game'] = self.object.game
        context['title'] = 'Update Task'
        context['submit_text'] = 'Save Changes'
        return context


class GameTaskDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Delete a task
    """
    model = GameTask
    template_name = 'projects/task_confirm_delete.html'
    context_object_name = 'task'
    
    def test_func(self):
        # Only allow task deletion by staff or the task creator
        return self.request.user.is_staff or self.get_object().assigned_to == self.request.user
    
    def get_success_url(self):
        messages.success(self.request, f"Task '{self.object.title}' deleted successfully!")
        return reverse_lazy('games:task_list', kwargs={'game_id': self.object.game.id})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['game'] = self.object.game
        context['today'] = date.today()
        return context


class GameTaskKanbanView(LoginRequiredMixin, ListView):
    """
    Kanban board view for tasks
    """
    model = GameTask
    template_name = 'projects/task_kanban.html'
    context_object_name = 'tasks'
    
    def get_queryset(self):
        queryset = GameTask.objects.all()
        
        # Filter by game if provided
        game_id = self.kwargs.get('game_id')
        if game_id:
            queryset = queryset.filter(game_id=game_id)
            
        # Filter by assigned user if requested
        if self.request.GET.get('my_tasks'):
            queryset = queryset.filter(assigned_to=self.request.user)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add game to context if filtering by game
        game_id = self.kwargs.get('game_id')
        if game_id:
            context['game'] = get_object_or_404(GameProject, id=game_id)
        
        # Group tasks by status for kanban columns
        tasks_by_status = {}
        for status, label in GameTask.STATUS_CHOICES:
            tasks_by_status[status] = self.get_queryset().filter(status=status).order_by('-priority', 'due_date')
        
        context['tasks_by_status'] = tasks_by_status
        context['status_choices'] = GameTask.STATUS_CHOICES
        context['today'] = date.today()
        
        return context

class GameTaskListView(LoginRequiredMixin, ListView):
    """
    List tasks for a game
    """
    model = GameTask
    template_name = 'projects/task_list.html'
    context_object_name = 'tasks'
    
    def get_queryset(self):
        queryset = GameTask.objects.all()
        
        # Filter by game if provided
        game_id = self.kwargs.get('game_id')
        if game_id:
            queryset = queryset.filter(game_id=game_id)
            
        # Filter by assigned user if requested
        if self.request.GET.get('my_tasks'):
            queryset = queryset.filter(assigned_to=self.request.user)
            
        # Filter by status if provided
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
            
        # Filter by task type if provided
        task_type = self.request.GET.get('type')
        if task_type:
            queryset = queryset.filter(task_type=task_type)
            
        return queryset.order_by('-priority', 'due_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add game to context if filtering by game
        game_id = self.kwargs.get('game_id')
        if game_id:
            context['game'] = get_object_or_404(GameProject, id=game_id)
            
        # Add task status counts for filters
        context['status_counts'] = {
            status[0]: GameTask.objects.filter(status=status[0]).count() 
            for status in GameTask.STATUS_CHOICES
        }
        
        # Add task type counts for filters
        context['type_counts'] = {
            task_type[0]: GameTask.objects.filter(task_type=task_type[0]).count() 
            for task_type in GameTask.TASK_TYPE_CHOICES
        }
        
        return context


class GameTaskDetailView(LoginRequiredMixin, DetailView):
    """
    View details of a specific task
    """
    model = GameTask
    template_name = 'projects/task_detail.html'
    context_object_name = 'task'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['game'] = self.object.game
        context['today'] = date.today()
        return context


class GameTaskCreateView(LoginRequiredMixin, CreateView):
    """
    Create a new task for a game
    """
    model = GameTask
    form_class = GameTaskForm
    template_name = 'projects/task_form.html'
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Limit milestone choices to the current game
        game_id = self.kwargs.get('game_id')
        if game_id:
            form.fields['milestone'].queryset = GameMilestone.objects.filter(game_id=game_id)
        return form
    
    def form_valid(self, form):
        # Set the game for this task
        game_id = self.kwargs.get('game_id')
        form.instance.game_id = game_id
        
        # Set the creator as the current user if not specified
        if not form.instance.assigned_to:
            form.instance.assigned_to = self.request.user
            
        messages.success(self.request, f"Task '{form.instance.title}' created successfully!")
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('games:task_list', kwargs={'game_id': self.object.game.id})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        game_id = self.kwargs.get('game_id')
        context['game'] = get_object_or_404(GameProject, id=game_id)
        context['title'] = 'Create New Task'
        context['submit_text'] = 'Create Task'
        return context


class GameTaskUpdateView(LoginRequiredMixin, UpdateView):
    """
    Update an existing task
    """
    model = GameTask
    form_class = GameTaskForm
    template_name = 'projects/task_form.html'
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Limit milestone choices to the current game
        form.fields['milestone'].queryset = GameMilestone.objects.filter(game=self.object.game)
        return form
    
    def form_valid(self, form):
        messages.success(self.request, f"Task '{form.instance.title}' updated successfully!")
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('games:task_detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['game'] = self.object.game
        context['title'] = 'Update Task'
        context['submit_text'] = 'Save Changes'
        return context


class GameTaskDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Delete a task
    """
    model = GameTask
    template_name = 'projects/task_confirm_delete.html'
    context_object_name = 'task'
    
    def test_func(self):
        # Only allow task deletion by staff or the task creator
        return self.request.user.is_staff or self.get_object().assigned_to == self.request.user
    
    def get_success_url(self):
        messages.success(self.request, f"Task '{self.object.title}' deleted successfully!")
        return reverse_lazy('games:task_list', kwargs={'game_id': self.object.game.id})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['game'] = self.object.game
        context['today'] = date.today()
        return context


class GameTaskKanbanView(LoginRequiredMixin, ListView):
    """
    Kanban board view for tasks
    """
    model = GameTask
    template_name = 'projects/task_kanban.html'
    context_object_name = 'tasks'
    
    def get_queryset(self):
        queryset = GameTask.objects.all()
        
        # Filter by game if provided
        game_id = self.kwargs.get('game_id')
        if game_id:
            queryset = queryset.filter(game_id=game_id)
            
        # Filter by assigned user if requested
        if self.request.GET.get('my_tasks'):
            queryset = queryset.filter(assigned_to=self.request.user)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add game to context if filtering by game
        game_id = self.kwargs.get('game_id')
        if game_id:
            context['game'] = get_object_or_404(GameProject, id=game_id)
        
        # Group tasks by status for kanban columns
        tasks_by_status = {}
        for status, label in GameTask.STATUS_CHOICES:
            tasks_by_status[status] = self.get_queryset().filter(status=status).order_by('-priority', 'due_date')
        
        context['tasks_by_status'] = tasks_by_status
        context['status_choices'] = GameTask.STATUS_CHOICES
        context['today'] = date.today()
        
        return context
