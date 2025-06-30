from django.shortcuts import render, HttpResponse, redirect
from django.views.generic import TemplateView, View, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q, F
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import Http404
from datetime import date, timedelta

# Import legacy views for backward compatibility
from .legacy_views import R1D3TaskDetailLegacyView, R1D3TaskUpdateLegacyView, R1D3TaskDeleteLegacyView

# Import model utilities
from .model_utils import get_task_model_map, get_task_type_for_model

# Import task models for dashboard stats
try:
    from projects.task_models import (
        R1D3Task, GameDevelopmentTask, EducationTask,
        SocialMediaTask, ArcadeTask, ThemeParkTask
    )
    from projects.game_models import GameTask
    TASK_MODELS_AVAILABLE = True
except ImportError:
    TASK_MODELS_AVAILABLE = False

# Import game project models for dashboard stats
try:
    from projects.game_models import GameProject
    GAME_MODELS_AVAILABLE = True
except ImportError:
    GAME_MODELS_AVAILABLE = False


class TestView(View):
    """Simple test view to verify server functionality"""
    def get(self, request):
        return HttpResponse('<h1>Django Server is Working!</h1><p>The R1D3 Game Development System is running.</p>')


class HomeView(TemplateView):
    """Home page view"""
    template_name = 'core/home.html'


class DashboardView(LoginRequiredMixin, TemplateView):
    """Main dashboard view"""
    template_name = 'core/dashboard.html'
    login_url = '/'  # Temporarily changed from '/accounts/login/' while allauth is disabled
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add game development stats if models are available
        if GAME_MODELS_AVAILABLE:
            # Count active game projects
            context['game_count'] = GameProject.objects.filter(
                status__in=['pre_production', 'production', 'alpha', 'beta']
            ).count()
            
            # Count open tasks
            context['task_count'] = GameTask.objects.filter(
                status__in=['to_do', 'in_progress', 'blocked']
            ).count()
            
            # Get tasks assigned to current user
            context['user_tasks'] = GameTask.objects.filter(
                assigned_to=self.request.user,
                status__in=['to_do', 'in_progress']
            ).order_by('-priority', 'due_date')[:5]
        
        return context


class GlobalTaskDashboardView(LoginRequiredMixin, View):
    """Global task dashboard view showing tasks from all company sections"""
    template_name = 'core/global_task_dashboard.html'
    login_url = '/'  # Temporarily changed from '/accounts/login/' while allauth is disabled
    
    def get(self, request):
        # Get filter parameters
        status_filter = request.GET.get('status', '')
        priority_filter = request.GET.get('priority', '')
        assigned_filter = request.GET.get('assigned_to', '')
        company_section_filter = request.GET.get('company_section', '')
        due_date_filter = request.GET.get('due_date', '')
        search_query = request.GET.get('search', '')
        
        # Get all tasks from all task models
        r1d3_tasks = list(R1D3Task.objects.all())
        print(f"R1D3Task count: {len(r1d3_tasks)}")
        
        game_tasks = list(GameDevelopmentTask.objects.all())
        print(f"GameDevelopmentTask count: {len(game_tasks)}")
        
        education_tasks = list(EducationTask.objects.all())
        print(f"EducationTask count: {len(education_tasks)}")
        
        social_media_tasks = list(SocialMediaTask.objects.all())
        print(f"SocialMediaTask count: {len(social_media_tasks)}")
        
        arcade_tasks = list(ArcadeTask.objects.all())
        print(f"ArcadeTask count: {len(arcade_tasks)}")
        
        theme_park_tasks = list(ThemeParkTask.objects.all())
        print(f"ThemeParkTask count: {len(theme_park_tasks)}")
        
        # Get tasks from the old GameTask model
        old_game_tasks = list(GameTask.objects.all())
        print(f"Old GameTask count: {len(old_game_tasks)}")
        
        # Add task_type information to each task
        for task in r1d3_tasks:
            task.task_type = 'r1d3'
        
        for task in game_tasks:
            task.task_type = 'game_development'
        
        for task in education_tasks:
            task.task_type = 'education'
        
        for task in social_media_tasks:
            task.task_type = 'social_media'
        
        for task in arcade_tasks:
            task.task_type = 'arcade'
        
        for task in theme_park_tasks:
            task.task_type = 'theme_park'
        
        for task in old_game_tasks:
            task.task_type = task.company_section if task.company_section else 'game_development'
        
        # Combine all tasks into a single list
        all_tasks = r1d3_tasks + game_tasks + education_tasks + social_media_tasks + arcade_tasks + theme_park_tasks + old_game_tasks
        print(f"Total tasks before filtering: {len(all_tasks)}")
        
        # Sort tasks by created_at (newest first)
        tasks = sorted(all_tasks, key=lambda x: x.created_at, reverse=True)
        
        # Apply filters - since we're working with a Python list, we need to filter manually
        filtered_tasks = tasks
        print(f"Tasks before filtering: {len(filtered_tasks)}")
        
        # Filter by status
        if status_filter and status_filter != 'all':
            filtered_tasks = [task for task in filtered_tasks if task.status == status_filter]
            print(f"Tasks after status filter '{status_filter}': {len(filtered_tasks)}")
        
        # Filter by priority
        if priority_filter and priority_filter != 'all':
            filtered_tasks = [task for task in filtered_tasks if task.priority == priority_filter]
            print(f"Tasks after priority filter '{priority_filter}': {len(filtered_tasks)}")
        
        # Filter by assigned_to
        if assigned_filter == 'me':
            filtered_tasks = [task for task in filtered_tasks if task.assigned_to == request.user]
            print(f"Tasks after assigned_to filter 'me': {len(filtered_tasks)}")
        elif assigned_filter == 'unassigned':
            filtered_tasks = [task for task in filtered_tasks if task.assigned_to is None]
            print(f"Tasks after assigned_to filter 'unassigned': {len(filtered_tasks)}")
        
        # For company section, we need to check the task_type attribute
        if company_section_filter:
            print(f"Applying company section filter: '{company_section_filter}'")
            # Use the task_type attribute we added to each task
            filtered_tasks = [task for task in filtered_tasks if task.task_type == company_section_filter]
            print(f"Tasks after company section filter '{company_section_filter}': {len(filtered_tasks)}")
        
        today = date.today()
        if due_date_filter == 'overdue':
            filtered_tasks = [task for task in filtered_tasks if task.due_date and task.due_date < today and task.status in ['to_do', 'in_progress', 'blocked']]
            print(f"Tasks after due_date filter 'overdue': {len(filtered_tasks)}")
        elif due_date_filter == 'today':
            filtered_tasks = [task for task in filtered_tasks if task.due_date and task.due_date == today]
            print(f"Tasks after due_date filter 'today': {len(filtered_tasks)}")
        elif due_date_filter == 'this_week':
            end_of_week = today + timedelta(days=(6 - today.weekday()))
            filtered_tasks = [task for task in filtered_tasks if task.due_date and today <= task.due_date <= end_of_week]
            print(f"Tasks after due_date filter 'this_week': {len(filtered_tasks)}")
        
        if search_query:
            filtered_tasks = [task for task in filtered_tasks if 
                             search_query.lower() in task.title.lower() or 
                             (task.description and search_query.lower() in task.description.lower())]
            print(f"Tasks after search query '{search_query}': {len(filtered_tasks)}")
            
        # Update tasks with filtered results
        tasks = filtered_tasks
        
        # Calculate task statistics from the combined task list
        today = date.today()
        task_stats = {
            'total': len(all_tasks),
            'to_do': len([t for t in all_tasks if t.status == 'to_do']),
            'in_progress': len([t for t in all_tasks if t.status == 'in_progress']),
            'in_review': len([t for t in all_tasks if t.status == 'in_review']),
            'done': len([t for t in all_tasks if t.status == 'done']),
            'backlog': len([t for t in all_tasks if t.status == 'backlog']),
            'blocked': len([t for t in all_tasks if t.status == 'blocked']),
            'overdue': len([t for t in all_tasks if t.due_date and t.due_date < today and t.status in ['to_do', 'in_progress', 'blocked']]),
        }
        
        # Calculate section statistics
        # Count GameTask objects by company section
        game_dev_count = len(game_tasks) + len([t for t in old_game_tasks if t.company_section == 'game_development'])
        education_count = len(education_tasks) + len([t for t in old_game_tasks if t.company_section == 'education'])
        social_media_count = len(social_media_tasks) + len([t for t in old_game_tasks if t.company_section == 'social_media'])
        arcade_count = len(arcade_tasks) + len([t for t in old_game_tasks if t.company_section == 'arcade'])
        theme_park_count = len(theme_park_tasks) + len([t for t in old_game_tasks if t.company_section == 'theme_park'])
        
        section_stats = [
            {'section_name': 'r1d3', 'count': len(r1d3_tasks)},
            {'section_name': 'game_development', 'count': game_dev_count},
            {'section_name': 'education', 'count': education_count},
            {'section_name': 'social_media', 'count': social_media_count},
            {'section_name': 'arcade', 'count': arcade_count},
            {'section_name': 'theme_park', 'count': theme_park_count},
        ]
        
        # Get recent and upcoming tasks
        recent_tasks = sorted([t for t in all_tasks if t.status == 'done'], key=lambda x: x.updated_at, reverse=True)[:5]
        upcoming_tasks = sorted([t for t in all_tasks if t.due_date and t.due_date >= today and t.status in ['to_do', 'in_progress']], key=lambda x: x.due_date)[:5]
        
        context = {
            'tasks': tasks,
            'task_stats': task_stats,
            'section_stats': section_stats,
            'recent_tasks': recent_tasks,
            'upcoming_tasks': upcoming_tasks,
            'today': date.today(),
            'status_filter': status_filter,
            'priority_filter': priority_filter,
            'assigned_filter': assigned_filter,
            'company_section_filter': company_section_filter,
            'due_date_filter': due_date_filter,
            'search_query': search_query,
        }
        
        return render(request, self.template_name, context)


class SocialMediaTaskDashboardView(LoginRequiredMixin, View):
    """Social Media task dashboard view showing tasks from the social media section"""
    template_name = 'core/social_task_dashboard.html'
    login_url = '/'
    
    def get(self, request):
        # Get filter parameters
        status_filter = request.GET.get('status', '')
        priority_filter = request.GET.get('priority', '')
        assigned_filter = request.GET.get('assigned_to', '')
        platform_filter = request.GET.get('platform', '')
        due_date_filter = request.GET.get('due_date', '')
        search_query = request.GET.get('search', '')
        
        # Start with all social media tasks
        tasks = GameTask.objects.filter(company_section='social_media')
        
        # Apply filters
        if status_filter:
            tasks = tasks.filter(status=status_filter)
        
        if priority_filter:
            tasks = tasks.filter(priority=priority_filter)
        
        if assigned_filter == 'me':
            tasks = tasks.filter(assigned_to=request.user)
        elif assigned_filter == 'unassigned':
            tasks = tasks.filter(assigned_to__isnull=True)
        
        if platform_filter:
            tasks = tasks.filter(platform=platform_filter)
        
        if due_date_filter == 'overdue':
            tasks = tasks.filter(due_date__lt=date.today(), status__in=['to_do', 'in_progress', 'blocked'])
        elif due_date_filter == 'today':
            tasks = tasks.filter(due_date=date.today())
        elif due_date_filter == 'this_week':
            today = date.today()
            end_of_week = today + timedelta(days=(6 - today.weekday()))
            tasks = tasks.filter(due_date__range=[today, end_of_week])
        
        if search_query:
            tasks = tasks.filter(Q(title__icontains=search_query) | Q(description__icontains=search_query))
        
        # Get task statistics
        task_stats = {
            'total': tasks.count(),
            'to_do': tasks.filter(status='to_do').count(),
            'in_progress': tasks.filter(status='in_progress').count(),
            'in_review': tasks.filter(status='in_review').count(),
            'done': tasks.filter(status='done').count(),
            'backlog': tasks.filter(status='backlog').count(),
            'blocked': tasks.filter(status='blocked').count(),
            'overdue': tasks.filter(due_date__lt=date.today(), status__in=['to_do', 'in_progress', 'blocked']).count(),
        }
        
        # Get tasks by social media platform
        platform_stats = {
            'twitter': tasks.filter(platform='twitter').count(),
            'instagram': tasks.filter(platform='instagram').count(),
            'facebook': tasks.filter(platform='facebook').count(),
            'youtube': tasks.filter(platform='youtube').count(),
            'linkedin': tasks.filter(platform='linkedin').count(),
            'tiktok': tasks.filter(platform='tiktok').count(),
        }
        
        # Get recent and upcoming tasks
        recent_tasks = tasks.filter(status='done').order_by('-updated_at')[:5]
        upcoming_tasks = tasks.filter(
            due_date__gte=date.today(),
            status__in=['to_do', 'in_progress']
        ).order_by('due_date')[:5]
        
        context = {
            'tasks': tasks,
            'task_stats': task_stats,
            'platform_stats': platform_stats,
            'recent_tasks': recent_tasks,
            'upcoming_tasks': upcoming_tasks,
            'today': date.today(),
            'status_filter': status_filter,
            'priority_filter': priority_filter,
            'assigned_filter': assigned_filter,
            'platform_filter': platform_filter,
            'due_date_filter': due_date_filter,
            'search_query': search_query,
            'current_filters': any([status_filter, priority_filter, assigned_filter, platform_filter, due_date_filter, search_query]),
        }
        
        return render(request, self.template_name, context)


class R1D3TaskCreateView(LoginRequiredMixin, CreateView):
    """
    Create a new R1D3 task from the global task dashboard.
    This view uses the R1D3Task model and form from the projects app.
    """
    template_name = 'projects/r1d3_task_form.html'
    login_url = '/'  # Redirect to home if not logged in
    
    def get_form_class(self):
        # Import here to avoid circular imports
        from projects.task_forms import R1D3TaskForm
        return R1D3TaskForm
    
    def get_model(self):
        # Import here to avoid circular imports
        from projects.task_models import R1D3Task
        return R1D3Task
    
    def form_valid(self, form):
        # Set the created_by field to the current user
        form.instance.created_by = self.request.user
        messages.success(self.request, f"R1D3 Task '{form.instance.title}' created successfully!")
        return super().form_valid(form)
    
    def get_success_url(self):
        # Redirect back to the global task dashboard
        return reverse_lazy('core:global_task_dashboard')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['section_name'] = "R1D3 Task"
        context['is_create'] = True
        return context


class R1D3TaskUpdateView(LoginRequiredMixin, UpdateView):
    """
    Update an existing task from the global task dashboard.
    This view uses the task_type parameter to determine which model to use.
    """
    template_name = 'projects/r1d3_task_form.html'
    login_url = '/'  # Redirect to home if not logged in
    context_object_name = 'task'
    
    def get_object(self, queryset=None):
        # Import task models here to avoid circular imports
        from projects.task_models import (
            R1D3Task, GameDevelopmentTask, EducationTask,
            SocialMediaTask, ArcadeTask, ThemeParkTask
        )
        
        task_id = self.kwargs.get('pk')
        task_type = self.kwargs.get('task_type')
        
        # Map task_type to model
        model_map = {
            'r1d3': R1D3Task,
            'game_development': GameDevelopmentTask,
            'education': EducationTask,
            'social_media': SocialMediaTask,
            'arcade': ArcadeTask,
            'theme_park': ThemeParkTask,
        }
        
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
            from projects.task_forms import GameDevelopmentTaskForm
            self.form_class = GameDevelopmentTaskForm
            self.template_name = 'projects/game_task_form.html'
            self.section_name = 'Game Development Task'
        elif model_name == 'EducationTask':
            from projects.task_forms import EducationTaskForm
            self.form_class = EducationTaskForm
            self.template_name = 'projects/education_task_form.html'
            self.section_name = 'Education Task'
        elif model_name == 'SocialMediaTask':
            from projects.task_forms import SocialMediaTaskForm
            self.form_class = SocialMediaTaskForm
            self.template_name = 'projects/social_media_task_form.html'
            self.section_name = 'Social Media Task'
        elif model_name == 'ArcadeTask':
            from projects.task_forms import ArcadeTaskForm
            self.form_class = ArcadeTaskForm
            self.template_name = 'projects/arcade_task_form.html'
            self.section_name = 'Arcade Task'
        elif model_name == 'ThemeParkTask':
            from projects.task_forms import ThemeParkTaskForm
            self.form_class = ThemeParkTaskForm
            self.template_name = 'projects/theme_park_task_form.html'
            self.section_name = 'Theme Park Task'
        else:  # Default to R1D3Task
            from projects.task_forms import R1D3TaskForm
            self.form_class = R1D3TaskForm
            self.template_name = 'projects/r1d3_task_form.html'
            self.section_name = 'R1D3 Task'
    
    def form_valid(self, form):
        messages.success(self.request, f"Task '{form.instance.title}' updated successfully!")
        return super().form_valid(form)
    
    def get_success_url(self):
        # Redirect back to the global task dashboard
        return reverse_lazy('core:global_task_dashboard')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['section_name'] = getattr(self, 'section_name', 'Task')
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
        # Import task models here to avoid circular imports
        from projects.task_models import (
            R1D3Task, GameDevelopmentTask, EducationTask,
            SocialMediaTask, ArcadeTask, ThemeParkTask
        )
        
        task_id = self.kwargs.get('pk')
        task_type = self.kwargs.get('task_type')
        
        # Map task_type to model
        model_map = {
            'r1d3': R1D3Task,
            'game_development': GameDevelopmentTask,
            'education': EducationTask,
            'social_media': SocialMediaTask,
            'arcade': ArcadeTask,
            'theme_park': ThemeParkTask,
        }
        
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
            self.template_name = 'projects/task_confirm_delete.html'
            self.section_name = 'Game Development Task'
            self.active_department = 'game_dev'
        elif model_name == 'EducationTask':
            self.template_name = 'projects/task_confirm_delete.html'
            self.section_name = 'Education Task'
            self.active_department = 'education'
        elif model_name == 'SocialMediaTask':
            self.template_name = 'projects/task_confirm_delete.html'
            self.section_name = 'Social Media Task'
            self.active_department = 'social_media'
        elif model_name == 'ArcadeTask':
            self.template_name = 'arcade/task_confirm_delete.html'
            self.section_name = 'Arcade Task'
            self.active_department = 'arcade'
        elif model_name == 'ThemeParkTask':
            self.template_name = 'projects/task_confirm_delete.html'
            self.section_name = 'Theme Park Task'
            self.active_department = 'theme_park'
        else:  # Default to R1D3Task
            self.template_name = 'projects/task_confirm_delete.html'
            self.section_name = 'R1D3 Task'
            self.active_department = 'r1d3'
    
    def delete(self, request, *args, **kwargs):
        task = self.get_object()
        task_title = task.title  # Store the title before deletion
        messages.success(request, f"{self.section_name} '{task_title}' deleted successfully!")
        return super().delete(request, *args, **kwargs)
    
    def get_success_url(self):
        # Redirect back to the global task dashboard
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
        # Import task models here to avoid circular imports
        from projects.task_models import (
            R1D3Task, GameDevelopmentTask, EducationTask,
            SocialMediaTask, ArcadeTask, ThemeParkTask
        )
        
        task_id = self.kwargs.get('pk')
        task_type = self.kwargs.get('task_type')
        
        # Map task_type to model
        model_map = {
            'r1d3': R1D3Task,
            'game_development': GameDevelopmentTask,
            'education': EducationTask,
            'social_media': SocialMediaTask,
            'arcade': ArcadeTask,
            'theme_park': ThemeParkTask,
        }
        
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
