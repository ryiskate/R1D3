"""
Git Database Sync Views for R1D3 Project
"""
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from .git_sync import GitSyncManager


@login_required
@require_http_methods(["POST"])
def sync_database(request):
    """
    Sync database with Git repository
    POST parameters:
    - commit_message: Optional message if there are local changes
    """
    sync_manager = GitSyncManager()
    commit_message = request.POST.get('commit_message', '')
    
    # Perform sync
    result = sync_manager.sync_database(commit_message if commit_message else None)
    
    return JsonResponse(result)


@login_required
@require_http_methods(["GET"])
def sync_status(request):
    """Get current sync status"""
    sync_manager = GitSyncManager()
    status = sync_manager.get_sync_status()
    
    return JsonResponse(status)


@login_required
@require_http_methods(["POST"])
def pull_database(request):
    """Pull latest database changes only"""
    sync_manager = GitSyncManager()
    result = sync_manager.pull_latest()
    
    return JsonResponse({
        'success': result['success'],
        'message': 'Database pulled successfully' if result['success'] else f"Pull failed: {result['error']}",
        'output': result['output']
    })
