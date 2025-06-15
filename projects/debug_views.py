from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .game_models import GameTask

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
    
    return render(request, 'projects/debug_tasks.html', {
        'tasks': tasks,
        'tasks_by_status': tasks_by_status,
    })
