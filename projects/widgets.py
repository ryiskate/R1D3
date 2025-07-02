from django import forms
from django.utils.html import format_html
from .models import Team

class TeamSelectWidget(forms.Select):
    """
    Custom widget for Team selection that displays team members
    """
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        # Handle ModelChoiceIteratorValue objects (Django 3.1+)
        if hasattr(value, 'value'):
            value = value.value
            
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        
        if value and value != '':
            try:
                # Convert to int to ensure we're dealing with a proper ID
                team_id = int(value)
                team = Team.objects.get(pk=team_id)
                members = team.get_members_display()
                option['label'] = members
            except (Team.DoesNotExist, ValueError, TypeError):
                pass
        return option
