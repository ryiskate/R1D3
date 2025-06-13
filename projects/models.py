from django.db import models
from django.contrib.auth.models import User
from core.models import TimeStampedModel
from strategy.models import Goal, Objective


class Project(TimeStampedModel):
    """
    Project model for managing company projects
    """
    STATUS_CHOICES = [
        ('planning', 'Planning'),
        ('active', 'Active'),
        ('on_hold', 'On Hold'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planning')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    start_date = models.DateField()
    end_date = models.DateField()
    budget = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='managed_projects')
    team_members = models.ManyToManyField(User, related_name='projects', blank=True)
    related_goals = models.ManyToManyField(Goal, related_name='projects', blank=True)
    related_objectives = models.ManyToManyField(Objective, related_name='projects', blank=True)
    
    def __str__(self):
        return self.name
    
    @property
    def is_active(self):
        return self.status == 'active'
    
    @property
    def is_completed(self):
        return self.status == 'completed'


class Milestone(TimeStampedModel):
    """
    Project milestones
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='milestones')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    due_date = models.DateField()
    is_completed = models.BooleanField(default=False)
    completion_date = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.project.name} - {self.title}"


class Task(TimeStampedModel):
    """
    Project tasks
    """
    STATUS_CHOICES = [
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
        ('urgent', 'Urgent'),
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    milestone = models.ForeignKey(Milestone, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='to_do')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks')
    due_date = models.DateField(null=True, blank=True)
    estimated_hours = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    actual_hours = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    
    def __str__(self):
        return self.title
    
    @property
    def is_completed(self):
        return self.status == 'done'


class Risk(TimeStampedModel):
    """
    Project risks
    """
    IMPACT_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('severe', 'Severe'),
    ]
    
    PROBABILITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('very_high', 'Very High'),
    ]
    
    STATUS_CHOICES = [
        ('identified', 'Identified'),
        ('assessed', 'Assessed'),
        ('mitigated', 'Mitigated'),
        ('resolved', 'Resolved'),
        ('accepted', 'Accepted'),
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='risks')
    title = models.CharField(max_length=200)
    description = models.TextField()
    impact = models.CharField(max_length=20, choices=IMPACT_CHOICES)
    probability = models.CharField(max_length=20, choices=PROBABILITY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='identified')
    mitigation_plan = models.TextField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='owned_risks')
    
    def __str__(self):
        return f"{self.project.name} - {self.title}"
    
    @property
    def risk_score(self):
        """Calculate risk score based on impact and probability"""
        impact_values = {'low': 1, 'medium': 2, 'high': 3, 'severe': 4}
        probability_values = {'low': 1, 'medium': 2, 'high': 3, 'very_high': 4}
        
        return impact_values.get(self.impact, 1) * probability_values.get(self.probability, 1)
