from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.http import JsonResponse, HttpResponse
from django.template.loader import get_template
from django.conf import settings
import os
from .game_models import GameTask
from .task_models import R1D3Task, GameDevelopmentTask, EducationTask, SocialMediaTask, ArcadeTask, ThemeParkTask

@login_required
def debug_tasks_view(request):
    """Debug view to check if tasks are being properly queried"""
    # Get all tasks assigned to the current user
    tasks = GameTask.objects.filter(assigned_to=request.user)
    
    # Get tasks by status
    tasks_by_status = {
        'backlog': tasks.filter(status='backlog').count(),
        'to_do': tasks.filter(status='to_do').count(),
        'in_progress': tasks.filter(status='in_progress').count(),
        'in_review': tasks.filter(status='in_review').count(),
        'done': tasks.filter(status='done').count(),
        'blocked': tasks.filter(status='blocked').count(),
    }
    
    context = {
        'tasks': tasks,
        'tasks_by_status': tasks_by_status,
    }
    
    return render(request, 'projects/debug_tasks.html', context)


@method_decorator(login_required, name='dispatch')
class DebugAllTasksView(ListView):
    """Debug view to check all task types"""
    template_name = 'projects/debug_tasks.html'
    context_object_name = 'tasks'
    
    def get_queryset(self):
        # Get tasks from all models
        r1d3_tasks = list(R1D3Task.objects.all())
        print(f"DEBUG - R1D3 tasks: {len(r1d3_tasks)} - {[task.title for task in r1d3_tasks]}")
        
        game_tasks = list(GameDevelopmentTask.objects.all())
        education_tasks = list(EducationTask.objects.all())
        social_media_tasks = list(SocialMediaTask.objects.all())
        arcade_tasks = list(ArcadeTask.objects.all())
        theme_park_tasks = list(ThemeParkTask.objects.all())
        
        # Combine all tasks
        all_tasks = r1d3_tasks + game_tasks + education_tasks + social_media_tasks + arcade_tasks + theme_park_tasks
        print(f"DEBUG - All tasks: {len(all_tasks)}")
        print(f"DEBUG - Task types: {[task.__class__.__name__ for task in all_tasks]}")
        
        return all_tasks


class DebugSidebarView(LoginRequiredMixin, View):
    """Debug view to help troubleshoot sidebar navigation issues"""
    
    def get(self, request, *args, **kwargs):
        return render(request, 'projects/debug_sidebar.html')


class TemplateDebugView(LoginRequiredMixin, View):
    """Debug view to identify which template is being used for a specific URL"""
    
    def get(self, request, *args, **kwargs):
        # Get all available templates
        template_dirs = []
        for template_config in settings.TEMPLATES:
            if 'DIRS' in template_config:
                template_dirs.extend(template_config['DIRS'])
        
        # Get all template paths
        all_templates = []
        for template_dir in template_dirs:
            for root, dirs, files in os.walk(template_dir):
                for file in files:
                    if file.endswith('.html'):
                        template_path = os.path.join(root, file)
                        relative_path = os.path.relpath(template_path, template_dir)
                        all_templates.append(relative_path)
        
        # Get app template dirs
        app_templates = []
        for app_config in settings.INSTALLED_APPS:
            if not app_config.startswith('django.'):
                app_name = app_config.split('.')[-1] if '.' in app_config else app_config
                app_template_dir = os.path.join(settings.BASE_DIR, app_name, 'templates')
                if os.path.exists(app_template_dir):
                    for root, dirs, files in os.walk(app_template_dir):
                        for file in files:
                            if file.endswith('.html'):
                                template_path = os.path.join(root, file)
                                relative_path = os.path.relpath(template_path, app_template_dir)
                                app_templates.append(f"{app_name}:{relative_path}")
        
        # Get all template loaders
        template_loaders = []
        for template_config in settings.TEMPLATES:
            if 'OPTIONS' in template_config and 'loaders' in template_config['OPTIONS']:
                template_loaders.extend(template_config['OPTIONS']['loaders'])
        
        # Get information about the all-tasks dashboard view
        from projects.all_tasks_views import AllTasksDashboardView
        dashboard_view = AllTasksDashboardView()
        dashboard_template = dashboard_view.template_name
        
        # Return debug information
        debug_info = {
            'template_dirs': template_dirs,
            'all_templates': all_templates[:50],  # Limit to 50 to avoid overwhelming response
            'app_templates': app_templates[:50],  # Limit to 50 to avoid overwhelming response
            'template_loaders': str(template_loaders),
            'dashboard_template': dashboard_template,
            'dashboard_view': str(dashboard_view.__class__),
        }
        
        return render(request, 'projects/template_debug.html', {'debug_info': debug_info})
