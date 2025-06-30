"""
Updated GlobalTaskDashboardView that uses the model_utils module for consistency.
"""
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.db.models import Q

from .model_utils import get_task_model_map, get_task_type_for_model

class GlobalTaskDashboardView(LoginRequiredMixin, View):
    """Global task dashboard view showing tasks from all company sections"""
    template_name = 'core/global_task_dashboard.html'
    login_url = '/'  # Redirect to home if not logged in
    
    def get(self, request):
        # Get filter parameters
        status_filter = request.GET.get('status', '')
        priority_filter = request.GET.get('priority', '')
        assigned_filter = request.GET.get('assigned_to', '')
        company_section_filter = request.GET.get('company_section', '')
        due_date_filter = request.GET.get('due_date', '')
        search_query = request.GET.get('search', '')
        
        # Get the model map from the utility function
        model_map = get_task_model_map()
        
        # Get all tasks from all task models
        all_tasks = []
        for task_type, model in model_map.items():
            tasks = list(model.objects.all())
            # Add task_type attribute to each task
            for task in tasks:
                task.task_type = task_type
            all_tasks.extend(tasks)
        
        # Get tasks from the old GameTask model if it exists
        try:
            from projects.models import GameTask
            old_game_tasks = list(GameTask.objects.all())
            # Add task_type attribute based on company_section
            for task in old_game_tasks:
                task.task_type = task.company_section if task.company_section else 'game_development'
            all_tasks.extend(old_game_tasks)
        except ImportError:
            # GameTask model might not exist in newer versions
            pass
        
        # Sort tasks by created_at (newest first)
        tasks = sorted(all_tasks, key=lambda x: x.created_at, reverse=True)
        
        # Apply filters - since we're working with a Python list, we need to filter manually
        filtered_tasks = tasks
        
        # Filter by status
        if status_filter and status_filter != 'all':
            filtered_tasks = [task for task in filtered_tasks if task.status == status_filter]
        
        # Filter by priority
        if priority_filter and priority_filter != 'all':
            filtered_tasks = [task for task in filtered_tasks if task.priority == priority_filter]
        
        # Filter by assigned_to
        if assigned_filter == 'me':
            filtered_tasks = [task for task in filtered_tasks if task.assigned_to == request.user]
        elif assigned_filter == 'unassigned':
            filtered_tasks = [task for task in filtered_tasks if task.assigned_to is None]
        elif assigned_filter and assigned_filter.isdigit():
            from django.contrib.auth.models import User
            try:
                user = User.objects.get(id=assigned_filter)
                filtered_tasks = [task for task in filtered_tasks if task.assigned_to == user]
            except User.DoesNotExist:
                pass
        
        # Filter by company section / task type
        if company_section_filter:
            filtered_tasks = [task for task in filtered_tasks if task.task_type == company_section_filter]
        
        # Filter by due date
        if due_date_filter:
            filtered_tasks = [task for task in filtered_tasks if task.due_date and task.due_date.strftime('%Y-%m-%d') == due_date_filter]
        
        # Filter by search query
        if search_query:
            filtered_tasks = [task for task in filtered_tasks if 
                             search_query.lower() in task.title.lower() or 
                             (task.description and search_query.lower() in task.description.lower())]
        
        # Prepare context for the template
        context = {
            'tasks': filtered_tasks,
            'status_filter': status_filter,
            'priority_filter': priority_filter,
            'assigned_filter': assigned_filter,
            'company_section_filter': company_section_filter,
            'due_date_filter': due_date_filter,
            'search_query': search_query,
            'current_filters': any([status_filter, priority_filter, assigned_filter, 
                                   company_section_filter, due_date_filter, search_query]),
            'active_department': 'r1d3',  # For navigation highlighting
        }
        
        # Add task counts by status for the dashboard stats
        context['total_tasks'] = len(tasks)
        context['todo_tasks'] = len([task for task in tasks if task.status == 'to_do'])
        context['in_progress_tasks'] = len([task for task in tasks if task.status == 'in_progress'])
        context['completed_tasks'] = len([task for task in tasks if task.status == 'completed'])
        
        # Add task counts by company section
        context['r1d3_tasks'] = len([task for task in tasks if task.task_type == 'r1d3'])
        context['game_dev_tasks'] = len([task for task in tasks if task.task_type == 'game_development'])
        context['education_tasks'] = len([task for task in tasks if task.task_type == 'education'])
        context['social_media_tasks'] = len([task for task in tasks if task.task_type == 'social_media'])
        context['arcade_tasks'] = len([task for task in tasks if task.task_type == 'arcade'])
        context['theme_park_tasks'] = len([task for task in tasks if task.task_type == 'theme_park'])
        
        return render(request, self.template_name, context)
