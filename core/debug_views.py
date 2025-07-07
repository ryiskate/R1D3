from django.http import JsonResponse
from django.contrib.auth.decorators import user_passes_test
from projects.game_models import GameMilestone

@user_passes_test(lambda u: u.is_staff)
def debug_milestones(request):
    """
    Debug endpoint to list all milestones in the system.
    Only accessible to staff users.
    """
    milestones = GameMilestone.objects.filter(is_completed=False).order_by('due_date')
    
    milestone_data = []
    for m in milestones:
        milestone_data.append({
            'id': m.id,
            'title': m.title,
            'game': m.game.title,
            'due_date': m.due_date.strftime('%Y-%m-%d'),
            'is_completed': m.is_completed,
        })
    
    return JsonResponse({
        'milestones': milestone_data,
        'count': len(milestone_data),
        'user': request.user.username,
        'authenticated': request.user.is_authenticated,
    })
