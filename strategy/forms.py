from django import forms
from .models import Vision, Goal, Objective, KeyResult, StrategyPhase, StrategyMilestone


class VisionForm(forms.ModelForm):
    class Meta:
        model = Vision
        fields = ['title', 'description', 'target_year', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }


class GoalForm(forms.ModelForm):
    class Meta:
        model = Goal
        fields = ['title', 'description', 'vision', 'timeframe', 'target_date', 'status']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'target_date': forms.DateInput(attrs={'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }


class ObjectiveForm(forms.ModelForm):
    class Meta:
        model = Objective
        fields = ['title', 'description', 'goal', 'owner', 'due_date', 'status']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }


class KeyResultForm(forms.ModelForm):
    class Meta:
        model = KeyResult
        fields = ['title', 'description', 'objective', 'target_value', 'current_value', 'unit']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class StrategyPhaseForm(forms.ModelForm):
    class Meta:
        model = StrategyPhase
        fields = ['name', 'phase_type', 'description', 'order', 'start_year', 'end_year', 'is_current', 'status']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'start_year': forms.NumberInput(attrs={'class': 'form-control'}),
            'end_year': forms.NumberInput(attrs={'class': 'form-control'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }


class StrategyMilestoneForm(forms.ModelForm):
    class Meta:
        model = StrategyMilestone
        fields = ['title', 'description', 'phase', 'target_date', 'status', 'completion_date', 'order']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'target_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'completion_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }
