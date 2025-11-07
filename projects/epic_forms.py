"""
Forms for Epic management
"""
from django import forms
from django.conf import settings
from .task_models import Epic


class EpicForm(forms.ModelForm):
    """
    Form for creating and editing epics
    """
    owner_name = forms.ChoiceField(
        required=False,
        label='Epic Owner',
        help_text='Select the team member who owns this epic'
    )
    
    class Meta:
        model = Epic
        fields = [
            'title', 'description', 'company_section', 'status', 'priority',
            'owner_name', 'start_date', 'target_date', 'tags'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describe the epic goals and scope...'}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'target_date': forms.DateInput(attrs={'type': 'date'}),
            'tags': forms.TextInput(attrs={'placeholder': 'Separate tags with commas'}),
        }
        labels = {
            'company_section': 'Department',
            'target_date': 'Target Completion Date',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set team member choices from settings
        self.fields['owner_name'].choices = settings.TEAM_MEMBERS
        
        # Add CSS classes
        for field_name, field in self.fields.items():
            if field_name not in ['description']:
                field.widget.attrs['class'] = 'form-control'
