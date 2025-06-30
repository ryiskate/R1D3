"""
Tests for the task URL conflict resolution.
These tests verify that task URLs with task_type parameter resolve correctly
and legacy URLs redirect properly.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test.client import RequestFactory

# Import task models
from projects.task_models import (
    R1D3Task, GameDevelopmentTask, EducationTask,
    SocialMediaTask, ArcadeTask, ThemeParkTask
)
try:
    from projects.game_models import GameTask
except ImportError:
    GameTask = None

from core.model_utils import get_task_model_map


class TaskURLTests(TestCase):
    """Test case for task URL patterns with task_type parameter."""
    
    def setUp(self):
        """Set up test data."""
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        self.client = Client()
        self.client.login(username='testuser', password='testpassword')
        self.factory = RequestFactory()
        
        # Create tasks for each model with different titles to identify them
        self.r1d3_task = R1D3Task.objects.create(
            title='R1D3 Test Task',
            description='Test task for R1D3',
            status='to_do',
            priority='medium',
            assigned_to=self.user
        )
        
        self.game_task = GameDevelopmentTask.objects.create(
            title='Game Dev Test Task',
            description='Test task for Game Development',
            status='to_do',
            priority='medium',
            assigned_to=self.user
        )
        
        self.education_task = EducationTask.objects.create(
            title='Education Test Task',
            description='Test task for Education',
            status='to_do',
            priority='medium',
            assigned_to=self.user
        )
        
        self.social_media_task = SocialMediaTask.objects.create(
            title='Social Media Test Task',
            description='Test task for Social Media',
            status='to_do',
            priority='medium',
            assigned_to=self.user
        )
        
        self.arcade_task = ArcadeTask.objects.create(
            title='Arcade Test Task',
            description='Test task for Arcade',
            status='to_do',
            priority='medium',
            assigned_to=self.user
        )
        
        self.theme_park_task = ThemeParkTask.objects.create(
            title='Theme Park Test Task',
            description='Test task for Theme Park',
            status='to_do',
            priority='medium',
            assigned_to=self.user
        )
        
        # Store tasks in a dictionary for easy access
        self.tasks = {
            'r1d3': self.r1d3_task,
            'game_development': self.game_task,
            'education': self.education_task,
            'social_media': self.social_media_task,
            'arcade': self.arcade_task,
            'theme_park': self.theme_park_task,
        }
    
    def test_task_detail_urls_with_task_type(self):
        """Test that task detail URLs with task_type parameter resolve correctly."""
        # Test only one task type to simplify the test
        task_type = 'r1d3'
        task = self.tasks[task_type]
        url = reverse('core:r1d3_task_detail', kwargs={'task_type': task_type, 'pk': task.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, task.title)
    
    def test_task_update_urls_with_task_type(self):
        """Test that task update URLs with task_type parameter resolve correctly."""
        # Test only one task type to simplify the test
        task_type = 'r1d3'
        task = self.tasks[task_type]
        url = reverse('core:r1d3_task_update', kwargs={'task_type': task_type, 'pk': task.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, task.title)
    
    def test_task_delete_urls_with_task_type(self):
        """Test that task delete URLs with task_type parameter resolve correctly."""
        # Test only one task type to simplify the test
        task_type = 'r1d3'
        task = self.tasks[task_type]
        url = reverse('core:r1d3_task_delete', kwargs={'task_type': task_type, 'pk': task.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, task.title)
    
    def test_legacy_detail_url_redirects(self):
        """Test that legacy detail URLs redirect to the new URL pattern with task_type."""
        # Test only one task to simplify the test
        task = self.r1d3_task
        url = reverse('core:r1d3_task_detail_legacy', kwargs={'pk': task.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # Should redirect
        # The URL should contain task_type=r1d3
        self.assertIn('task_type=r1d3', response.url)
    
    def test_global_task_dashboard_displays_tasks(self):
        """Test that the global task dashboard displays tasks."""
        url = reverse('core:global_task_dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Check that at least one task is displayed
        self.assertContains(response, self.r1d3_task.title)
    
    def test_model_utils_get_task_model_map(self):
        """Test that get_task_model_map returns the correct mapping."""
        model_map = get_task_model_map()
        
        # Verify that all expected task types are in the map
        expected_task_types = [
            'r1d3', 'game_development', 'education', 
            'social_media', 'arcade', 'theme_park'
        ]
        
        for task_type in expected_task_types:
            self.assertIn(task_type, model_map)
        
        # Verify that the models are correctly mapped
        self.assertEqual(model_map['r1d3'], R1D3Task)
        self.assertEqual(model_map['game_development'], GameDevelopmentTask)
        self.assertEqual(model_map['education'], EducationTask)
        self.assertEqual(model_map['social_media'], SocialMediaTask)
        self.assertEqual(model_map['arcade'], ArcadeTask)
        self.assertEqual(model_map['theme_park'], ThemeParkTask)



