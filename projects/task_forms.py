from django import forms
from django.contrib.auth.models import User
from django.forms import inlineformset_factory, formset_factory
from .task_models import (
    BaseTask, R1D3Task, GameDevelopmentTask, EducationTask,
    SocialMediaTask, ArcadeTask, ThemeParkTask, SubTask
)
from .game_models import GameMilestone
from .widgets import TeamSelectWidget


class SubTaskForm(forms.ModelForm):
    """
    Form for subtasks
    """
    class Meta:
        model = SubTask
        fields = ['title', 'is_completed']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control subtask-title', 'placeholder': 'Enter subtask'}),
        }


class BaseTaskForm(forms.ModelForm):
    """
    Base form for all task types with common fields
    """
    class Meta:
        model = BaseTask
        fields = [
            'title', 'description', 'task_type', 'status', 'priority',
            'assigned_to', 'due_date', 'has_additional_note', 'additional_note_text',
            'has_subtasks', 'output'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'additional_note_text': forms.Textarea(attrs={'rows': 2, 'class': 'additional-note-field'}),
            'output': forms.Textarea(attrs={'rows': 4, 'class': 'output-field'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Check if this is a ThemeParkTaskForm and remove estimated_hours if it exists
        if self.__class__.__name__ == 'ThemeParkTaskForm' and 'estimated_hours' in self.fields:
            del self.fields['estimated_hours']


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
        fields = BaseTaskForm.Meta.fields + ['team', 'gdd_section', 'platform']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set game and milestone fields to None since they're not in the form
        if self.instance:
            self.instance.game = None
            self.instance.milestone = None
            
        # Make sure team field is properly configured
        if 'team' in self.fields:
            from .models import Team
            self.fields['team'].queryset = Team.objects.all().order_by('name')
            self.fields['team'].empty_label = 'No team assigned'


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
        fields = BaseTaskForm.Meta.fields + ['platform', 'campaign_id', 'channel', 'target_metrics', 'content_type']


class ArcadeTaskForm(BaseTaskForm):
    """
    Form for arcade tasks - excludes estimated_hours field
    """
    class Meta(BaseTaskForm.Meta):
        model = ArcadeTask
        fields = ['title', 'description', 'task_type', 'status', 'priority',
                 'assigned_to', 'due_date', 'machine_id', 'location', 'maintenance_type',
                 'has_additional_note', 'additional_note_text', 'has_subtasks', 'output']
        exclude = ['estimated_hours']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ensure estimated_hours is removed from the form fields
        if 'estimated_hours' in self.fields:
            del self.fields['estimated_hours']


class ThemeParkTaskForm(BaseTaskForm):
    """
    Form for theme park tasks - excludes estimated_hours field
    """
    class Meta(BaseTaskForm.Meta):
        model = ThemeParkTask
        fields = ['title', 'description', 'task_type', 'status', 'priority',
                 'assigned_to', 'due_date', 'attraction_id', 'zone', 'safety_priority',
                 'has_additional_note', 'additional_note_text', 'has_subtasks', 'output']
        exclude = ['estimated_hours']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ensure estimated_hours is removed from the form fields
        if 'estimated_hours' in self.fields:
            del self.fields['estimated_hours']


# Create a formset for subtasks
SubTaskFormSet = formset_factory(
    SubTaskForm,
    extra=3,  # Start with 3 empty forms
    can_delete=True,
    max_num=10  # Maximum of 10 subtasks
)
