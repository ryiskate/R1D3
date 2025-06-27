from django import forms
from .models import Project, Milestone, Task, Risk, GameTask, GameMilestone, GDDSection


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description', 'status', 'priority', 'start_date', 'end_date', 
                 'budget', 'manager', 'team_members', 'related_goals', 'related_objectives']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'team_members': forms.SelectMultiple(attrs={'class': 'select2'}),
            'related_goals': forms.SelectMultiple(attrs={'class': 'select2'}),
            'related_objectives': forms.SelectMultiple(attrs={'class': 'select2'}),
        }


class MilestoneForm(forms.ModelForm):
    class Meta:
        model = Milestone
        fields = ['project', 'title', 'description', 'due_date', 'is_completed', 'completion_date']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'completion_date': forms.DateInput(attrs={'type': 'date'}),
        }


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['project', 'milestone', 'title', 'description', 'status', 'priority',
                 'assigned_to', 'due_date', 'estimated_hours', 'actual_hours']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }


class RiskForm(forms.ModelForm):
    class Meta:
        model = Risk
        fields = ['project', 'title', 'description', 'impact', 'probability', 
                 'status', 'mitigation_plan', 'owner']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'mitigation_plan': forms.Textarea(attrs={'rows': 3}),
        }


class GameTaskForm(forms.ModelForm):
    class Meta:
        model = GameTask
        fields = [
            'title', 'description', 'status', 'priority', 
            'assigned_to', 'due_date', 'estimated_hours', 
            'actual_hours', 'milestone', 'company_section',
            'gdd_section', 'feature_id', 'platform',
            'course_id', 'learning_objective', 'target_audience',
            'machine_id', 'location', 'maintenance_type',
            'campaign_id', 'channel', 'target_metrics',
            'research_area', 'experiment_id', 'hypothesis'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set up milestone queryset based on game association
        if hasattr(self.instance, 'game') and self.instance.game:
            self.fields['milestone'].queryset = GameMilestone.objects.filter(game=self.instance.game)
        else:
            self.fields['milestone'].queryset = GameMilestone.objects.none()
            
        # Set up GDD section queryset
        self.fields['gdd_section'].queryset = GDDSection.objects.all()
        
        # Set date input format
        self.fields['due_date'].input_formats = ['%Y-%m-%d']
