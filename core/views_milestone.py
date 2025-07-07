from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.core.cache import cache
from django.db import connection
from django.views.decorators.csrf import csrf_exempt

@login_required
def get_milestone_display(request):
    """
    AJAX endpoint to get the current milestone display HTML.
    This is used to update the milestone display without refreshing the page.
    """
    # Clear any cached data to ensure we get fresh milestone data
    cache.clear()
    
    # Reset database connection to ensure fresh queries
    connection.close()
    
    # Force database connection to be closed and reopened
    from django.db import connection
    connection.close()
    
    # Import models directly to ensure fresh queries
    from projects.game_models import GameMilestone
    from django.utils import timezone
    
    # Get the milestone data from the context processor
    from core.context_processors import breadcrumbs_processor
    
    # Force a fresh context
    context_data = breadcrumbs_processor(request)
    
    # Add a timestamp to force template refresh
    import time
    context_data['refresh_timestamp'] = time.time()
    
    # Render the milestone display HTML directly
    html = ''
    if context_data.get('in_progress_milestone') and context_data.get('company_phase'):
        milestone = context_data['in_progress_milestone']
        phase = context_data['company_phase']
        
        # Determine the background gradient based on phase type
        bg_style = ''
        if phase.phase_type == 'indie_dev':
            bg_style = 'background: linear-gradient(135deg, #4e73df 0%, #224abe 100%);'
        elif phase.phase_type == 'arcade':
            bg_style = 'background: linear-gradient(135deg, #1cc88a 0%, #13855c 100%);'
        elif phase.phase_type == 'theme_park':
            bg_style = 'background: linear-gradient(135deg, #f6c23e 0%, #dda20a 100%);'
        else:
            bg_style = 'background: linear-gradient(135deg, #4e73df 0%, #224abe 100%);'
        
        # Build the HTML
        html = f'''
        <div class="d-inline-block py-2 px-3 rounded" style="{bg_style}">
            <span class="text-white">
                <i class="fas fa-flag me-1"></i>
                <span class="fw-bold">Company Phase {phase.order}:</span>
                <span class="ms-1">"{phase.name}" - "{milestone.title}"</span>
                <!-- Refresh timestamp: {time.time()} -->
            </span>
        </div>
        '''
    elif context_data.get('in_progress_milestone'):
        milestone = context_data['in_progress_milestone']
        html = f'''
        <div class="d-inline-block py-2 px-3 rounded" style="background: linear-gradient(135deg, #4e73df 0%, #224abe 100%);">
            <span class="text-white">
                <i class="fas fa-flag me-1"></i>
                <span class="fw-bold">Current Milestone:</span>
                <span class="ms-1">"{milestone.title}"</span>
            </span>
        </div>
        '''
    else:
        html = '''
        <div class="d-inline-block py-2 px-3 rounded" style="background: linear-gradient(135deg, #4e73df 0%, #224abe 100%);">
            <span class="text-white">
                <i class="fas fa-flag me-1"></i>
                <span class="fw-bold">Company Phase:</span>
                <span class="ms-1">No active milestone</span>
            </span>
        </div>
        '''
    
    # Return the HTML as a response
    return HttpResponse(html)


@csrf_exempt
def test_milestone_update(request):
    """
    Test endpoint to verify that milestone updates are working correctly.
    This endpoint will return the current milestone data as JSON.
    """
    # Clear any cached data to ensure we get fresh milestone data
    cache.clear()
    
    # Reset database connection to ensure fresh queries
    connection.close()
    
    # Get the milestone data from the context processor
    from core.context_processors import breadcrumbs_processor
    context_data = breadcrumbs_processor(request)
    
    # Extract the milestone data
    milestone_data = {
        'timestamp': context_data.get('milestone_debug', {}).get('timestamp', None),
        'in_progress_milestone': None,
        'company_phase': None,
    }
    
    # Add milestone data if available
    if context_data.get('in_progress_milestone'):
        milestone = context_data['in_progress_milestone']
        milestone_data['in_progress_milestone'] = {
            'id': milestone.id,
            'title': milestone.title,
            'due_date': str(milestone.due_date),
            'is_completed': milestone.is_completed,
        }
    
    # Add company phase data if available
    if context_data.get('company_phase'):
        phase = context_data['company_phase']
        milestone_data['company_phase'] = {
            'id': phase.id,
            'name': phase.name,
            'phase_type': phase.phase_type,
            'order': phase.order,
        }
    
    # Return the data as JSON
    return JsonResponse(milestone_data)
