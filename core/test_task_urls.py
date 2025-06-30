from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from projects.task_models import (
    R1D3Task, GameDevelopmentTask, EducationTask,
    SocialMediaTask, ArcadeTask, ThemeParkTask
)

class TaskURLTests(TestCase):
    """
    Test case for verifying task URL resolution with task_type parameter.
    """
    
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        # Create test tasks for each model
        self.r1d3_task = R1D3Task.objects.create(
            title='Test R1D3 Task',
            description='Test description',
            created_by=self.user
        )
        
        self.game_task = GameDevelopmentTask.objects.create(
            title='Test Game Task',
            description='Test description',
            created_by=self.user
        )
        
        self.education_task = EducationTask.objects.create(
            title='Test Education Task',
            description='Test description',
            created_by=self.user
        )
        
        self.social_media_task = SocialMediaTask.objects.create(
            title='Test Social Media Task',
            description='Test description',
            created_by=self.user
        )
        
        self.arcade_task = ArcadeTask.objects.create(
            title='Test Arcade Task',
            description='Test description',
            created_by=self.user
        )
        
        self.theme_park_task = ThemeParkTask.objects.create(
            title='Test Theme Park Task',
            description='Test description',
            created_by=self.user
        )
        
        # Create a client and log in
        self.client = Client()
        self.client.login(username='testuser', password='testpassword')
    
    def test_task_detail_urls(self):
        """Test that task detail URLs with task_type parameter work correctly."""
        # Test each task type
        task_types = {
            'r1d3': self.r1d3_task,
            'game_development': self.game_task,
            'education': self.education_task,
            'social_media': self.social_media_task,
            'arcade': self.arcade_task,
            'theme_park': self.theme_park_task
        }
        
        for task_type, task in task_types.items():
            url = reverse('core:r1d3_task_detail', kwargs={'task_type': task_type, 'pk': task.id})
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, task.title)
    
    def test_task_update_urls(self):
        """Test that task update URLs with task_type parameter work correctly."""
        # Test each task type
        task_types = {
            'r1d3': self.r1d3_task,
            'game_development': self.game_task,
            'education': self.education_task,
            'social_media': self.social_media_task,
            'arcade': self.arcade_task,
            'theme_park': self.theme_park_task
        }
        
        for task_type, task in task_types.items():
            url = reverse('core:r1d3_task_update', kwargs={'task_type': task_type, 'pk': task.id})
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, task.title)
    
    def test_task_delete_urls(self):
        """Test that task delete URLs with task_type parameter work correctly."""
        # Test each task type
        task_types = {
            'r1d3': self.r1d3_task,
            'game_development': self.game_task,
            'education': self.education_task,
            'social_media': self.social_media_task,
            'arcade': self.arcade_task,
            'theme_park': self.theme_park_task
        }
        
        for task_type, task in task_types.items():
            url = reverse('core:r1d3_task_delete', kwargs={'task_type': task_type, 'pk': task.id})
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, task.title)
    
    def test_legacy_urls(self):
        """Test that legacy URLs without task_type parameter redirect correctly."""
        # Test each task type
        task_types = {
            'r1d3': self.r1d3_task,
            'game_development': self.game_task,
            'education': self.education_task,
            'social_media': self.social_media_task,
            'arcade': self.arcade_task,
            'theme_park': self.theme_park_task
        }
        
        for task_type, task in task_types.items():
            # Test detail legacy URL
            url = reverse('core:r1d3_task_detail_legacy', kwargs={'pk': task.id})
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)  # Should redirect
            
            # Test update legacy URL
            url = reverse('core:r1d3_task_update_legacy', kwargs={'pk': task.id})
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)  # Should redirect
            
            # Test delete legacy URL
            url = reverse('core:r1d3_task_delete_legacy', kwargs={'pk': task.id})
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)  # Should redirect
