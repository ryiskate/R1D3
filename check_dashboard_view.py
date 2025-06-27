import os
import django
import sys

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'company_system.settings')
django.setup()

# Import models and views after Django setup
from django.contrib.auth.models import User
from django.test import RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth.middleware import AuthenticationMiddleware
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.messages.storage.fallback import FallbackStorage

from projects.game_models import GameTask, GameProject
from projects.task_models import (
    R1D3Task, GameDevelopmentTask, EducationTask,
    SocialMediaTask, ArcadeTask, ThemeParkTask
)
from core.views import GlobalTaskDashboardView

def add_middleware_to_request(request, user=None):
    """Add session/auth/messages middleware to the request"""
    middleware = SessionMiddleware(lambda x: None)
    middleware.process_request(request)
    request.session.save()
    
    middleware = AuthenticationMiddleware(lambda x: None)
    middleware.process_request(request)
    
    middleware = MessageMiddleware(lambda x: None)
    middleware.process_request(request)
    request._messages = FallbackStorage(request)
    
    if user:
        request.user = user
    
    return request

def check_dashboard_view():
    print("\n=== CHECKING DASHBOARD VIEW ===")
    
    # Create a request factory
    factory = RequestFactory()
    
    # Get or create a test user
    user, created = User.objects.get_or_create(
        username='admin',
        defaults={'is_staff': True, 'is_superuser': True}
    )
    if created:
        user.set_password('admin')
        user.save()
        print(f"Created test user: {user.username}")
    else:
        print(f"Using existing user: {user.username}")
    
    # Create a request
    request = factory.get('/dashboard/')
    request = add_middleware_to_request(request, user)
    
    # Get the view
    view = GlobalTaskDashboardView.as_view()
    
    # Call the view
    response = view(request)
    
    # Check the context
    context = response.context_data
    
    # Print task counts
    print(f"\nDashboard tasks count: {len(context['tasks'])}")
    
    # Print task statistics
    print("\nTask Statistics:")
    for key, value in context['task_stats'].items():
        print(f"- {key}: {value}")
    
    # Print section statistics
    print("\nSection Statistics:")
    for section in context['section_stats']:
        print(f"- {section['section_name']}: {section['count']}")
    
    # Print tasks by type
    task_types = {}
    for task in context['tasks']:
        task_type = task.__class__.__name__
        if task_type not in task_types:
            task_types[task_type] = []
        task_types[task_type].append(task)
    
    print("\nTasks by Type:")
    for task_type, tasks in task_types.items():
        print(f"- {task_type}: {len(tasks)}")
        for task in tasks[:3]:  # Show first 3 tasks of each type
            print(f"  * {task.id}: {task.title}")
        if len(tasks) > 3:
            print(f"  * ... and {len(tasks) - 3} more")

if __name__ == "__main__":
    check_dashboard_view()
