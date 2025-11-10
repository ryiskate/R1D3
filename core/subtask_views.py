"""
Subtask API views for toggling completion status
"""
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from core.task_utils import get_subtask_by_id


@login_required
@require_POST
def toggle_subtask(request, subtask_id):
    """Toggle subtask completion status"""
    try:
        # Get the subtask
        subtask = get_subtask_by_id(subtask_id)
        
        if not subtask:
            return JsonResponse({
                'success': False,
                'error': 'Subtask not found'
            }, status=404)
        
        # Get the new status from request
        is_completed = request.POST.get('is_completed', 'false').lower() == 'true'
        
        # Update the subtask
        subtask.is_completed = is_completed
        subtask.save()
        
        return JsonResponse({
            'success': True,
            'subtask_id': subtask_id,
            'is_completed': is_completed
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
