from django import forms
from .gdd_models import MultiGDD, GDDSection, GameDesignDocumentType, GDDComment

class MultiGDDForm(forms.ModelForm):
    """
    Form for creating and editing Game Design Documents
    """
    class Meta:
        model = MultiGDD
        fields = [
            'title', 'version', 'gdd_type',
            'high_concept', 'player_experience', 'core_mechanics',
            'game_rules', 'controls', 'story_synopsis', 'world_building',
            'art_style', 'audio_style', 'technical_requirements',
            'monetization', 'marketing', 'is_published'
        ]
        widgets = {
            'high_concept': forms.Textarea(attrs={'rows': 3}),
            'player_experience': forms.Textarea(attrs={'rows': 3}),
            'core_mechanics': forms.Textarea(attrs={'rows': 5}),
            'game_rules': forms.Textarea(attrs={'rows': 5}),
            'controls': forms.Textarea(attrs={'rows': 3}),
            'story_synopsis': forms.Textarea(attrs={'rows': 5}),
            'world_building': forms.Textarea(attrs={'rows': 5}),
            'art_style': forms.Textarea(attrs={'rows': 3}),
            'audio_style': forms.Textarea(attrs={'rows': 3}),
            'technical_requirements': forms.Textarea(attrs={'rows': 3}),
            'monetization': forms.Textarea(attrs={'rows': 3}),
            'marketing': forms.Textarea(attrs={'rows': 3}),
        }

class GDDSectionForm(forms.ModelForm):
    """
    Form for creating and editing GDD sections
    """
    class Meta:
        model = GDDSection
        fields = ['title', 'content', 'section_id', 'order']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 5}),
        }

class GDDCommentForm(forms.ModelForm):
    """
    Form for adding comments to GDD sections
    """
    class Meta:
        model = GDDComment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Add a comment...'}),
        }
