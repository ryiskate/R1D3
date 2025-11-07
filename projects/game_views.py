import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.db.models import Q, Sum, Count
from django.utils import timezone
from datetime import date

from .task_models import GameDevelopmentTask
from .task_forms import GameDevelopmentTaskForm
from .game_models import (
    GameProject, GameDesignDocument, GameAsset, GameMilestone, 
    GameTask, GameBuild, PlaytestSession, PlaytestFeedback, GameBug
)
from .models import Team
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
        # Use GameDevelopmentTask model instead of GameTask for user's tasks
        from .task_models import GameDevelopmentTask
        
        # Get current profile name from session
        current_user_name = self.request.session.get('current_user_name', '')
        
        if current_user_name:
            context['my_tasks'] = GameDevelopmentTask.objects.filter(
                Q(assigned_to_name=current_user_name) | Q(created_by_name=current_user_name),
                status__in=['backlog', 'to_do', 'in_progress', 'in_review', 'blocked']
            ).order_by('due_date', '-priority')[:10]  # Limit to 10 most relevant tasks
        else:
            context['my_tasks'] = GameDevelopmentTask.objects.filter(
                assigned_to=self.request.user,
                status__in=['backlog', 'to_do', 'in_progress', 'in_review', 'blocked']
            ).order_by('due_date', '-priority')[:10]  # Limit to 10 most relevant tasks
        # Use GameDevelopmentTask model for overdue tasks as well
        if current_user_name:
            context['overdue_tasks'] = GameDevelopmentTask.objects.filter(
                Q(assigned_to_name=current_user_name) | Q(created_by_name=current_user_name),
                due_date__lt=timezone.now().date(),
                status__in=['to_do', 'in_progress', 'in_review', 'blocked']
            ).order_by('due_date')
        else:
            context['overdue_tasks'] = GameDevelopmentTask.objects.filter(
                due_date__lt=timezone.now().date(),
                status__in=['to_do', 'in_progress', 'in_review', 'blocked']
            ).order_by('due_date')
        context['recent_builds'] = GameBuild.objects.order_by('-build_date')[:5]
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
        
        # Get game tasks - using GameDevelopmentTask instead of GameTask
        from .task_models import GameDevelopmentTask
        tasks = GameDevelopmentTask.objects.filter(game=game).order_by('-priority', 'due_date')
        context['tasks'] = tasks
        
        # Count tasks by status
        task_counts = {
            'backlog': GameDevelopmentTask.objects.filter(game=game, status='backlog').count(),
            'to_do': GameDevelopmentTask.objects.filter(game=game, status='to_do').count(),
            'in_progress': GameDevelopmentTask.objects.filter(game=game, status='in_progress').count(),
            'in_review': GameDevelopmentTask.objects.filter(game=game, status='in_review').count(),
            'done': GameDevelopmentTask.objects.filter(game=game, status='done').count(),
            'blocked': GameDevelopmentTask.objects.filter(game=game, status='blocked').count(),
        }
        
        # Calculate percentages for the progress bars
        total_tasks = sum(task_counts.values())
        if total_tasks > 0:
            context['tasks_by_status'] = {
                status: int((count / total_tasks) * 100) 
                for status, count in task_counts.items()
            }
        else:
            context['tasks_by_status'] = {status: 0 for status in task_counts}
        
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
















class GameDesignDocumentView(LoginRequiredMixin, DetailView):
    """
    View a game design document with support for HTML content and task integration
    The view expects the game's ID, not the GDD's ID
    """
    model = GameDesignDocument
    template_name = 'projects/gdd_detail_simple.html'
    context_object_name = 'gdd'
    
    def get_object(self, queryset=None):
        """
        Get the GDD by the game ID instead of the GDD ID
        """
        if queryset is None:
            queryset = self.get_queryset()
            
        # Get the game ID from the URL
        game_id = self.kwargs.get('pk')
        
        # Look up the GDD by the game ID
        try:
            # Get the game first
            from projects.game_models import GameProject
            game = GameProject.objects.get(id=game_id)
            
            # Then get the GDD for this game
            return queryset.get(game=game)
        except (GameProject.DoesNotExist, GameDesignDocument.DoesNotExist):
            raise Http404("No game design document found for this game")

    
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
        
        # Use ensure_ascii=False to handle non-ASCII characters properly and escape HTML entities
        from django.utils.html import escapejs
        context['sections_json'] = escapejs(json.dumps(sections_json, ensure_ascii=False))
        
        sections_with_tasks_json = {}
        for section_id, tasks in sections_with_tasks.items():
            # Convert section_id to string to ensure it's a valid JSON key
            str_section_id = str(section_id)
            sections_with_tasks_json[str_section_id] = [{
                'id': task.id,
                'title': task.title,
                'status_display': task.get_status_display()
            } for task in tasks]
        
        # Use ensure_ascii=False to handle non-ASCII characters properly and escape HTML entities
        context['sections_with_tasks_json'] = escapejs(json.dumps(sections_with_tasks_json, ensure_ascii=False))
        
        # Get all tasks for the game for the task management panel
        context['all_game_tasks'] = GameTask.objects.filter(game=game).select_related('gdd_feature')
        
        # Return the context
        return context
















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
















class GameDesignDocumentCreateView(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    Create a game design document or redirect to edit if one already exists.
    This view now redirects to the structured GDD creation interface for a better user experience.
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
            # Redirect to the structured edit interface instead of the HTML editor
            return redirect('games:gdd_structured_edit', pk=existing_gdd.id)
        except GameDesignDocument.DoesNotExist:
            # No GDD exists, redirect to the structured creation interface
            messages.info(request, "Create a new Game Design Document using the user-friendly interface.")
            return redirect('games:gdd_structured_create', game_id=game_id)
    
    def post(self, request, *args, **kwargs):
        # This method should not be called directly anymore since we're redirecting in get()
        # But we'll keep it for backward compatibility
        game_id = self.kwargs.get('game_id')
        game = get_object_or_404(GameProject, id=game_id)
        
        # Check if a GDD already exists for this game
        try:
            existing_gdd = GameDesignDocument.objects.get(game=game)
            messages.error(request, "A Game Design Document already exists for this game. You cannot create another one.")
            return redirect('games:gdd_structured_edit', pk=existing_gdd.id)
        except GameDesignDocument.DoesNotExist:
            # Redirect to the structured creation interface
            return redirect('games:gdd_structured_create', game_id=game_id)


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
















# GameTaskDashboardView has been moved to game_task_dashboard_view.py
# This reduces code duplication and centralizes the dashboard functionality


class GameTaskDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Delete a game development task
    """
    model = GameDevelopmentTask
    template_name = 'projects/task_confirm_delete.html'
    context_object_name = 'task'
    
    def test_func(self):
        # Only allow task deletion by staff or the task creator
        task = self.get_object()
        return self.request.user.is_staff or (task.assigned_to == self.request.user) or (task.created_by == self.request.user)
    
    def get_success_url(self):
        messages.success(self.request, f"Task '{self.object.title}' deleted successfully!")
        # Redirect to the game task dashboard after deletion
        if hasattr(self.object, 'game') and self.object.game:
            return reverse_lazy('games:game_task_dashboard', kwargs={'game_id': self.object.game.id})
        return reverse_lazy('games:task_dashboard')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Safely add the game to context if it exists
        if hasattr(self.object, 'game') and self.object.game:
            context['game'] = self.object.game
        else:
            context['game'] = None
        context['today'] = date.today()
        return context


class GameTaskKanbanView(LoginRequiredMixin, ListView):
    """
    Kanban board view for game development tasks
    """
    model = GameDevelopmentTask
    template_name = 'projects/task_kanban.html'
    context_object_name = 'tasks'
    
    def get_queryset(self):
        queryset = GameDevelopmentTask.objects.all()
        
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
        for status, label in self.model.STATUS_CHOICES:
            tasks_by_status[status] = self.get_queryset().filter(status=status).order_by('-priority', 'due_date')
        
        context['tasks_by_status'] = tasks_by_status
        context['status_choices'] = GameTask.STATUS_CHOICES
        context['today'] = date.today()
        
        return context


class GameTaskCreateView(LoginRequiredMixin, CreateView):
    """
    Create a new game development task for a game
    """
    model = GameDevelopmentTask
    form_class = GameDevelopmentTaskForm
    template_name = 'projects/game_task_form.html'
    
    def get_success_url(self):
        messages.success(self.request, f"Task '{self.object.title}' created successfully!")
        return reverse_lazy('games:game_task_dashboard', kwargs={'game_id': self.object.game.id})
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Add game_id to form kwargs for filtering related fields
        kwargs['game_id'] = self.kwargs.get('game_id')
        return kwargs
    
    def form_valid(self, form):
        # Set the game for the task
        form.instance.game_id = self.kwargs.get('game_id')
        # Set the created_by field to the current user
        form.instance.created_by = self.request.user
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        game_id = self.kwargs.get('game_id')
        context['game'] = get_object_or_404(GameProject, id=game_id)
        context['today'] = date.today()
        context['teams'] = Team.objects.all().order_by('name')
        return context


class GameTaskDetailView(LoginRequiredMixin, DetailView):
    """
    View details of a specific game development task
    """
    model = GameDevelopmentTask
    template_name = 'projects/task_detail.html'
    context_object_name = 'task'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Only set game in context if it exists
        if hasattr(self.object, 'game') and self.object.game is not None:
            context['game'] = self.object.game
        else:
            context['game'] = None
            
        context['status_choices'] = self.model.STATUS_CHOICES
        context['priority_choices'] = self.model.PRIORITY_CHOICES
        context['today'] = date.today()
        
        # Get related tasks
        if hasattr(self.object, 'related_tasks') and self.object.related_tasks.exists():
            context['related_tasks'] = self.object.related_tasks.all()
        
        # Get task comments
        if hasattr(self.object, 'comments'):
            context['comments'] = self.object.comments.order_by('-created_at')
        
        # Get subtasks for this task
        if self.object.has_subtasks:
            from django.contrib.contenttypes.models import ContentType
            from projects.task_models import SubTask
            
            content_type = ContentType.objects.get_for_model(self.object)
            subtasks = SubTask.objects.filter(
                content_type=content_type,
                object_id=self.object.id
            )
            context['subtasks'] = subtasks
        
        return context


from .base_task_views import BaseTaskUpdateView

class GameTaskUpdateView(BaseTaskUpdateView):
    """
    Update an existing game development task
    """
    model = GameDevelopmentTask
    form_class = GameDevelopmentTaskForm
    template_name = 'projects/game_task_form.html'
    section_name = "Game Development Task"
    
    def get_success_url(self):
        messages.success(self.request, f"{self.section_name} '{self.object.title}' updated successfully!")
        return reverse_lazy('games:task_detail', kwargs={'pk': self.object.pk})
    
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
        context['teams'] = Team.objects.all().order_by('name')
        
        # Add subtasks to the context
        if self.object.has_subtasks:
            from django.contrib.contenttypes.models import ContentType
            from projects.task_models import SubTask
            
            content_type = ContentType.objects.get_for_model(self.object)
            subtasks = SubTask.objects.filter(
                content_type=content_type,
                object_id=self.object.id
            )
            context['subtasks'] = subtasks
            
        return context


# GameTaskListView has been removed as it's been replaced by GameTaskDashboardView
# This reduces potential security vulnerabilities from unused views
