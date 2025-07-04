from django.db import models
from core.models import TimeStampedModel
from django.contrib.auth.models import User


class Vision(TimeStampedModel):
    """
    Company vision statement and long-term goals
    """
    title = models.CharField(max_length=200)
    description = models.TextField()
    target_year = models.IntegerField(help_text="Target year for achieving this vision")
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.title} ({self.target_year})"


class Goal(TimeStampedModel):
    """
    Strategic goals aligned with the company vision
    """
    TIMEFRAME_CHOICES = [
        ('short', 'Short-term (< 1 year)'),
        ('medium', 'Medium-term (1-3 years)'),
        ('long', 'Long-term (3+ years)'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    vision = models.ForeignKey(Vision, on_delete=models.CASCADE, related_name='goals')
    timeframe = models.CharField(max_length=10, choices=TIMEFRAME_CHOICES)
    target_date = models.DateField()
    is_completed = models.BooleanField(default=False)
    
    def __str__(self):
        return self.title


class Objective(TimeStampedModel):
    """
    Specific objectives (OKRs) related to strategic goals
    """
    title = models.CharField(max_length=200)
    description = models.TextField()
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE, related_name='objectives')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_objectives')
    due_date = models.DateField()
    is_completed = models.BooleanField(default=False)
    
    def __str__(self):
        return self.title


class KeyResult(TimeStampedModel):
    """
    Measurable key results for objectives (part of OKR methodology)
    """
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    objective = models.ForeignKey(Objective, on_delete=models.CASCADE, related_name='key_results')
    target_value = models.FloatField(help_text="Target numerical value to achieve")
    current_value = models.FloatField(default=0, help_text="Current progress towards target")
    unit = models.CharField(max_length=50, help_text="Unit of measurement (%, $, etc.)")
    
    def __str__(self):
        return self.title
    
    @property
    def progress_percentage(self):
        """Calculate percentage of completion"""
        if self.target_value == 0:
            return 0
        return min(100, (self.current_value / self.target_value) * 100)


class StrategyPhase(TimeStampedModel):
    """
    Represents a phase in the company's growth strategy roadmap
    """
    PHASE_CHOICES = [
        ('indie_dev', 'Indie Game Development'),
        ('arcade', 'Arcade Machines'),
        ('theme_park', 'Theme Park Attractions'),
    ]
    
    name = models.CharField(max_length=100)
    phase_type = models.CharField(max_length=20, choices=PHASE_CHOICES)
    description = models.TextField()
    order = models.PositiveIntegerField(help_text="Order in the roadmap sequence")
    start_year = models.IntegerField(help_text="Estimated start year")
    end_year = models.IntegerField(help_text="Estimated completion year")
    is_current = models.BooleanField(default=False, help_text="Is this the current active phase?")
    is_completed = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return self.name


class StrategyMilestone(TimeStampedModel):
    """
    Key milestones within a strategy phase
    """
    title = models.CharField(max_length=200)
    description = models.TextField()
    phase = models.ForeignKey(StrategyPhase, on_delete=models.CASCADE, related_name='milestones')
    target_date = models.DateField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    completion_date = models.DateField(null=True, blank=True)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return self.title
