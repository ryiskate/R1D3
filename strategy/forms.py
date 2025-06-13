from django import forms
from .models import Vision, Goal, Objective, KeyResult


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
        fields = ['title', 'description', 'vision', 'timeframe', 'target_date', 'is_completed']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'target_date': forms.DateInput(attrs={'type': 'date'}),
        }


class ObjectiveForm(forms.ModelForm):
    class Meta:
        model = Objective
        fields = ['title', 'description', 'goal', 'owner', 'due_date', 'is_completed']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }


class KeyResultForm(forms.ModelForm):
    class Meta:
        model = KeyResult
        fields = ['title', 'description', 'objective', 'target_value', 'current_value', 'unit']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
