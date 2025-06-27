from django.shortcuts import render
from django.views.generic import View
from projects.task_models import EducationTask

class DebugEducationTasksView(View):
    """Simple view to debug education tasks"""
    
    def get(self, request, *args, **kwargs):
        # Get all education tasks
        tasks = EducationTask.objects.all()
        
        # Print debug info
        print(f"DEBUG: Found {tasks.count()} education tasks")
        for task in tasks[:5]:
            print(f"DEBUG: Task {task.id}: {task.title} (Status: {task.status})")
        
        # Create simple context
        context = {
            'tasks': tasks,
            'task_count': tasks.count()
        }
        
        return render(request, 'education/debug_tasks.html', context)
