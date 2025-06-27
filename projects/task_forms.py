from django import forms
from django.contrib.auth.models import User
from .task_models import (
    BaseTask, R1D3Task, GameDevelopmentTask, EducationTask,
    SocialMediaTask, ArcadeTask, ThemeParkTask
)
from .game_models import GameMilestone


class BaseTaskForm(forms.ModelForm):
    """
    Base form for all task types with common fields
    """
    class Meta:
        model = BaseTask
        fields = [
            'title', 'description', 'task_type', 'status', 'priority',
            'assigned_to', 'due_date', 'estimated_hours', 'actual_hours'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }


class R1D3TaskForm(BaseTaskForm):
    """
    Form for general R1D3 company tasks
    """
    class Meta(BaseTaskForm.Meta):
        model = R1D3Task
        fields = BaseTaskForm.Meta.fields + ['department', 'impact_level', 'strategic_goal']


class GameDevelopmentTaskForm(BaseTaskForm):
    """
    Form for game development tasks linked to specific games
    """
    class Meta(BaseTaskForm.Meta):
        model = GameDevelopmentTask
        fields = BaseTaskForm.Meta.fields + ['game', 'milestone', 'gdd_section', 'feature_id', 'platform']
        
    def __init__(self, *args, **kwargs):
        game_id = kwargs.pop('game_id', None)
        super().__init__(*args, **kwargs)
        
        # Filter milestones by game if game_id is provided
        if game_id and 'milestone' in self.fields:
            self.fields['milestone'].queryset = GameMilestone.objects.filter(game_id=game_id)
        elif self.instance and hasattr(self.instance, 'game') and self.instance.game:
            self.fields['milestone'].queryset = GameMilestone.objects.filter(game=self.instance.game)


class GameDevelopmentSectionTaskForm(BaseTaskForm):
    """
    Form for general game development section tasks (not tied to specific games)
    """
    class Meta(BaseTaskForm.Meta):
        model = GameDevelopmentTask
        fields = BaseTaskForm.Meta.fields + ['gdd_section', 'platform']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set game and milestone fields to None since they're not in the form
        if self.instance:
            self.instance.game = None
            self.instance.milestone = None


class EducationTaskForm(BaseTaskForm):
    """
    Form for education tasks
    """
    class Meta(BaseTaskForm.Meta):
        model = EducationTask
        fields = BaseTaskForm.Meta.fields + ['course_id', 'learning_objective', 'target_audience']


class SocialMediaTaskForm(BaseTaskForm):
    """
    Form for social media tasks
    """
    class Meta(BaseTaskForm.Meta):
        model = SocialMediaTask
        fields = BaseTaskForm.Meta.fields + ['campaign_id', 'channel', 'target_metrics']


class ArcadeTaskForm(BaseTaskForm):
    """
    Form for arcade tasks
    """
    class Meta(BaseTaskForm.Meta):
        model = ArcadeTask
        fields = BaseTaskForm.Meta.fields + ['machine_id', 'location', 'maintenance_type']


class ThemeParkTaskForm(BaseTaskForm):
    """
    Form for theme park tasks
    """
    class Meta(BaseTaskForm.Meta):
        model = ThemeParkTask
        fields = BaseTaskForm.Meta.fields + ['attraction_id', 'zone', 'safety_priority']
