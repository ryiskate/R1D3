from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from .models import Team

User = get_user_model()

class BaseTask(models.Model):
    """
    Abstract base class for all task types in the R1D3 system.
    Contains fields common to all tasks regardless of department.
    """
    # Core task fields
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Status and priority
    STATUS_CHOICES = [
        ('backlog', 'Backlog'),
        ('to_do', 'To Do'),
        ('in_progress', 'In Progress'),
        ('in_review', 'In Review'),
        ('done', 'Done'),
        ('blocked', 'Blocked'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='to_do')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    
    # Dates
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    due_date = models.DateField(null=True, blank=True)
    
    # Assignment
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, 
        null=True, related_name='%(class)s_created'
    )
    assigned_to = models.ForeignKey(
        User, on_delete=models.SET_NULL, 
        null=True, blank=True, related_name='%(class)s_assigned'
    )
    # Re-enabled team field
    team = models.ForeignKey(
        'projects.Team', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='%(class)s_tasks'
    )
    
    # Time tracking
    estimated_hours = models.DecimalField(max_digits=5, decimal_places=1, default=0)
    actual_hours = models.DecimalField(max_digits=5, decimal_places=1, default=0)
    
    # Tags and categorization
    tags = models.CharField(max_length=255, blank=True)
    
    # Task type for categorization
    task_type = models.CharField(max_length=100, blank=True)
    
    # Additional fields for notes and subtasks
    has_additional_note = models.BooleanField(default=False, verbose_name="Add additional note")
    additional_note_text = models.TextField(blank=True, null=True, verbose_name="Additional note")
    has_subtasks = models.BooleanField(default=False, verbose_name="Add subtasks")
    output = models.TextField(blank=True, null=True, verbose_name="Output")
    
    class Meta:
        abstract = True
        ordering = ['-priority', 'due_date', 'title']
    
    def __str__(self):
        return self.title
    
    def is_overdue(self):
        if self.due_date and self.status not in ['done', 'blocked']:
            return self.due_date < timezone.now().date()
        return False
    
    def get_completion_percentage(self):
        """Calculate task completion percentage based on status"""
        status_percentages = {
            'backlog': 0,
            'to_do': 0,
            'in_progress': 50,
            'in_review': 80,
            'done': 100,
            'blocked': 30,
        }
        return status_percentages.get(self.status, 0)
        

class SubTask(models.Model):
    """
    Model for subtasks that can be added to any task type
    Uses a generic foreign key to associate with any task model
    """
    # Link to parent task (any task model)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    parent_task = GenericForeignKey('content_type', 'object_id')
    
    # Subtask details
    title = models.CharField(max_length=255)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
        verbose_name = 'Subtask'
        verbose_name_plural = 'Subtasks'
        
    def __str__(self):
        return self.title


class R1D3Task(BaseTask):
    """
    General R1D3 company tasks not specific to any department
    """
    # R1D3 specific fields
    department = models.CharField(max_length=100, blank=True)
    impact_level = models.CharField(max_length=50, blank=True)
    strategic_goal = models.CharField(max_length=255, blank=True)
    
    class Meta:
        verbose_name = "R1D3 Task"
        verbose_name_plural = "R1D3 Tasks"


class GameDevelopmentTask(BaseTask):
    """
    Tasks specific to game development department
    """
    # Game reference
    game = models.ForeignKey(
        'GameProject', on_delete=models.SET_NULL, 
        null=True, blank=True, related_name='game_tasks'
    )
    
    # Game development specific fields
    gdd_section = models.ForeignKey(
        'GDDSection', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='game_dev_tasks'
    )
    milestone = models.ForeignKey(
        'GameMilestone', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='game_dev_tasks'
    )
    feature_id = models.CharField(max_length=100, blank=True)
    platform = models.CharField(max_length=100, blank=True)
    build_version = models.CharField(max_length=50, blank=True)
    
    class Meta:
        verbose_name = "Game Development Task"
        verbose_name_plural = "Game Development Tasks"


class EducationTask(BaseTask):
    """
    Tasks specific to the education department
    """
    course_id = models.CharField(max_length=100, blank=True)
    learning_objective = models.TextField(blank=True)
    target_audience = models.CharField(max_length=100, blank=True)
    educational_level = models.CharField(max_length=50, blank=True)
    
    class Meta:
        verbose_name = "Education Task"
        verbose_name_plural = "Education Tasks"


class SocialMediaTask(BaseTask):
    """
    Tasks specific to social media management
    """
    platform = models.CharField(max_length=50, blank=True)
    campaign_id = models.CharField(max_length=100, blank=True)
    channel = models.CharField(max_length=100, blank=True)
    target_metrics = models.TextField(blank=True)
    content_type = models.CharField(max_length=50, blank=True)
    
    class Meta:
        verbose_name = "Social Media Task"
        verbose_name_plural = "Social Media Tasks"


class ArcadeTask(BaseTask):
    """
    Tasks specific to arcade management
    """
    machine_id = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=255, blank=True)
    maintenance_type = models.CharField(max_length=100, blank=True)
    machine_model = models.CharField(max_length=100, blank=True)
    
    class Meta:
        verbose_name = "Arcade Task"
        verbose_name_plural = "Arcade Tasks"


class ThemeParkTask(BaseTask):
    """
    Tasks specific to theme park operations
    """
    attraction_id = models.CharField(max_length=100, blank=True)
    zone = models.CharField(max_length=100, blank=True)
    task_type = models.CharField(max_length=100, blank=True)
    safety_priority = models.CharField(max_length=50, blank=True)
    
    class Meta:
        verbose_name = "Theme Park Task"
        verbose_name_plural = "Theme Park Tasks"
