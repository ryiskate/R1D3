from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
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
            status__in=['to_do', 'in_progress']
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
            '2d_art': game.assets.filter(asset_type='2d_art').count(),
            '3d_model': game.assets.filter(asset_type='3d_model').count(),
            'animation': game.assets.filter(asset_type='animation').count(),
            'sound': game.assets.filter(asset_type='sound').count(),
            'music': game.assets.filter(asset_type='music').count(),
            'code': game.assets.filter(asset_type='code').count(),
        }
        
        # Get game builds
        context['builds'] = game.builds.all().order_by('-build_date')
        
        # Get bugs
        context['bugs'] = game.bugs.all().order_by('-severity')
        context['open_bugs'] = game.bugs.filter(status__in=['open', 'confirmed', 'in_progress']).count()
        
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
    View a game design document
    """
    model = GameDesignDocument
    template_name = 'projects/gdd_detail.html'
    context_object_name = 'gdd'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['game'] = self.object.game
        context['today'] = date.today()
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

class GameDesignDocumentCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """
    Create a game design document
    """
    model = GameDesignDocument
    form_class = GameDesignDocumentForm
    template_name = 'projects/gdd_form.html'
    
    def test_func(self):
        # Only allow staff or game leads to create GDDs
        game_id = self.kwargs.get('game_id')
        game = get_object_or_404(GameProject, id=game_id)
        return self.request.user.is_staff or self.request.user == game.lead_developer or self.request.user == game.lead_designer
    
    def form_valid(self, form):
        game_id = self.kwargs.get('game_id')
        form.instance.game = get_object_or_404(GameProject, id=game_id)
        messages.success(self.request, "Game Design Document created successfully!")
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('projects:game_detail', kwargs={'pk': self.object.game.id})


class GameAssetListView(LoginRequiredMixin, ListView):
    """
    List assets for a game
    """
    model = GameAsset
    template_name = 'projects/asset_list.html'
    context_object_name = 'assets'
    
    def get_queryset(self):
        game_id = self.kwargs.get('game_id')
        return GameAsset.objects.filter(game_id=game_id)
    
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
        return reverse_lazy('projects:asset_list', kwargs={'game_id': self.object.game.id})
    
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
