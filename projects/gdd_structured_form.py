"""
Structured forms for creating and editing Game Design Documents with sections and features.
This provides a user-friendly interface without requiring HTML editing.
"""
from django import forms
from django.forms import inlineformset_factory, BaseInlineFormSet, formset_factory
from .game_models import GameDesignDocument, GDDSection, GDDFeature

class GDDStructuredForm(forms.ModelForm):
    """
    Form for creating and editing Game Design Documents with a structured approach
    """
    class Meta:
        model = GameDesignDocument
        fields = ['high_concept', 'game']
        widgets = {
            'high_concept': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'High Concept', 'rows': 3})
        }

class GDDSectionStructuredForm(forms.ModelForm):
    """
    Form for creating and editing GDD sections with a structured approach
    """
    class Meta:
        model = GDDSection
        fields = ['title', 'content', 'section_id', 'order']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Section Title'}),
            'content': forms.Textarea(attrs={'rows': 5, 'class': 'form-control', 'placeholder': 'Section Content'}),
            'section_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Section ID (e.g., gameplay, characters)'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Display Order'})
        }

class GDDSubsectionForm(forms.Form):
    """
    Form for creating and editing subsections within a GDD section
    """
    title = forms.CharField(max_length=255, widget=forms.TextInput(attrs={
        'class': 'form-control', 
        'placeholder': 'Subsection Title'
    }))
    
    content = forms.CharField(required=False, widget=forms.Textarea(attrs={
        'rows': 3, 
        'class': 'form-control', 
        'placeholder': 'Subsection Content'
    }))
    
    order = forms.IntegerField(widget=forms.NumberInput(attrs={
        'class': 'form-control', 
        'placeholder': 'Display Order'
    }))
    
    subsection_id = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-control', 
        'placeholder': 'Subsection ID (e.g., high-concept, core-mechanics)'
    }))

class GDDFeatureStructuredForm(forms.ModelForm):
    """
    Form for creating and editing GDD features with task management fields
    """
    PRIORITY_CHOICES = [
        ('critical', 'Critical'),
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low')
    ]
    
    STATUS_CHOICES = [
        ('to_do', 'To Do'),
        ('backlog', 'Backlog'),
        ('in_progress', 'In Progress'),
        ('in_review', 'In Review'),
        ('done', 'Done')
    ]
    
    feature_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control', 
        'placeholder': 'Feature Name'
    }))
    
    description = forms.CharField(widget=forms.Textarea(attrs={
        'rows': 3, 
        'class': 'form-control', 
        'placeholder': 'Feature Description'
    }))
    
    priority = forms.ChoiceField(choices=PRIORITY_CHOICES, widget=forms.Select(attrs={
        'class': 'form-control'
    }))
    
    status = forms.ChoiceField(choices=STATUS_CHOICES, required=False, widget=forms.Select(attrs={
        'class': 'form-control'
    }))
    
    task_id = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control', 
        'placeholder': 'Task ID'
    }))
    
    assigned_to = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control', 
        'placeholder': 'Assigned To'
    }))
    
    due_date = forms.DateField(required=False, widget=forms.DateInput(attrs={
        'class': 'form-control',
        'type': 'date',
        'placeholder': 'Due Date'
    }))
    
    order = forms.IntegerField(required=False, widget=forms.HiddenInput(attrs={
        'class': 'feature-order'
    }))
    
    class Meta:
        model = GDDFeature
        fields = ['feature_name', 'description', 'priority', 'status', 'task_id', 'assigned_to', 'due_date', 'order', 'subsection_id']
        widgets = {
            'feature_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Feature Name'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Feature Description'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'order': forms.HiddenInput(attrs={'class': 'feature-order'}),
            'subsection_id': forms.HiddenInput()
        }

class BaseFeatureFormSet(BaseInlineFormSet):
    """
    Base formset for GDD features that ensures proper validation
    """
    def clean(self):
        super().clean()
        # Validate that feature names are unique within a section
        feature_names = []
        for form in self.forms:
            if self.can_delete and self._should_delete_form(form):
                continue
            feature_name = form.cleaned_data.get('feature_name')
            if feature_name in feature_names:
                form.add_error('feature_name', 'Feature names must be unique within a section')
            feature_names.append(feature_name)

# Create formsets for sections and features
GDDSectionFormSet = inlineformset_factory(
    GameDesignDocument, 
    GDDSection,
    form=GDDSectionStructuredForm,
    extra=1,
    can_delete=True
)

GDDFeatureFormSet = inlineformset_factory(
    GDDSection,
    GDDFeature,
    form=GDDFeatureStructuredForm,
    formset=BaseFeatureFormSet,
    extra=1,
    can_delete=True
)

# Create a formset for subsections (not tied to a model)
GDDSubsectionFormSet = formset_factory(
    GDDSubsectionForm,
    extra=1,
    can_delete=True
)

# Define the standard GDD sections based on the template
STANDARD_GDD_SECTIONS = [
    {
        'title': '1. Game Overview',
        'section_id': 'game-overview',
        'order': 1,
        'subsections': [
            {'title': '1.1 High Concept', 'subsection_id': 'high-concept', 'order': 1},
            {'title': '1.2 Target Audience', 'subsection_id': 'target-audience', 'order': 2},
            {'title': '1.3 Unique Selling Points', 'subsection_id': 'unique-selling-points', 'order': 3},
            {'title': '1.4 Platforms', 'subsection_id': 'platforms', 'order': 4}
        ]
    },
    {
        'title': '2. Gameplay',
        'section_id': 'gameplay',
        'order': 2,
        'subsections': [
            {'title': '2.1 Core Mechanics', 'subsection_id': 'core-mechanics', 'order': 1},
            {'title': '2.2 Controls', 'subsection_id': 'controls', 'order': 2},
            {'title': '2.3 Progression Systems', 'subsection_id': 'progression-systems', 'order': 3},
            {'title': '2.4 Game Economy', 'subsection_id': 'game-economy', 'order': 4}
        ]
    },
    {
        'title': '3. Game World',
        'section_id': 'game-world',
        'order': 3,
        'subsections': [
            {'title': '3.1 World Overview', 'subsection_id': 'world-overview', 'order': 1},
            {'title': '3.2 Environments', 'subsection_id': 'environments', 'order': 2},
            {'title': '3.3 Level Design', 'subsection_id': 'level-design', 'order': 3},
            {'title': '3.4 World Interaction', 'subsection_id': 'world-interaction', 'order': 4}
        ]
    },
    {
        'title': '4. Characters',
        'section_id': 'characters',
        'order': 4,
        'subsections': [
            {'title': '4.1 Player Characters', 'subsection_id': 'player-characters', 'order': 1},
            {'title': '4.2 Non-Player Characters', 'subsection_id': 'non-player-characters', 'order': 2},
            {'title': '4.3 Enemies', 'subsection_id': 'enemies', 'order': 3},
            {'title': '4.4 Character Relationships', 'subsection_id': 'character-relationships', 'order': 4}
        ]
    },
    {
        'title': '5. Narrative',
        'section_id': 'narrative',
        'order': 5,
        'subsections': [
            {'title': '5.1 Story Overview', 'subsection_id': 'story-overview', 'order': 1},
            {'title': '5.2 Narrative Structure', 'subsection_id': 'narrative-structure', 'order': 2},
            {'title': '5.3 Storytelling Methods', 'subsection_id': 'storytelling-methods', 'order': 3},
            {'title': '5.4 Player Choice & Consequences', 'subsection_id': 'player-choice', 'order': 4}
        ]
    },
    {
        'title': '6. Technical Requirements',
        'section_id': 'technical-requirements',
        'order': 6,
        'subsections': [
            {'title': '6.1 Platform-Specific Requirements', 'subsection_id': 'platform-specific-requirements', 'order': 1}
        ]
    },
    {
        'title': '7. Audio Design',
        'section_id': 'audio-design',
        'order': 7,
        'subsections': [
            {'title': '7.1 Music', 'subsection_id': 'music', 'order': 1},
            {'title': '7.2 Sound Effects', 'subsection_id': 'sound-effects', 'order': 2},
            {'title': '7.3 Voice Acting', 'subsection_id': 'voice-acting', 'order': 3},
            {'title': '7.4 Audio Implementation', 'subsection_id': 'audio-implementation', 'order': 4}
        ]
    },
    {
        'title': '8. User Interface & UX',
        'section_id': 'user-interface',
        'order': 8,
        'subsections': [
            {'title': '8.1 UI Design', 'subsection_id': 'ui-design', 'order': 1},
            {'title': '8.2 HUD', 'subsection_id': 'hud', 'order': 2},
            {'title': '8.3 Menus', 'subsection_id': 'menus', 'order': 3},
            {'title': '8.4 Accessibility', 'subsection_id': 'accessibility', 'order': 4}
        ]
    },
    {
        'title': '9. Art Direction',
        'section_id': 'art-direction',
        'order': 9,
        'subsections': [
            {'title': '9.1 Visual Style', 'subsection_id': 'visual-style', 'order': 1},
            {'title': '9.2 Character Art', 'subsection_id': 'character-art', 'order': 2},
            {'title': '9.3 Environment Art', 'subsection_id': 'environment-art', 'order': 3},
            {'title': '9.4 Visual Effects', 'subsection_id': 'visual-effects', 'order': 4}
        ]
    },
    {
        'title': '10. Monetization',
        'section_id': 'monetization',
        'order': 10,
        'subsections': [
            {'title': '10.1 Revenue Model', 'subsection_id': 'revenue-model', 'order': 1},
            {'title': '10.2 In-Game Purchases', 'subsection_id': 'in-game-purchases', 'order': 2},
            {'title': '10.3 Monetization Balance', 'subsection_id': 'monetization-balance', 'order': 3},
            {'title': '10.4 Additional Revenue', 'subsection_id': 'additional-revenue', 'order': 4}
        ]
    },
    {
        'title': '11. Development & Production',
        'section_id': 'development',
        'order': 11,
        'subsections': [
            {'title': '11.1 Development Roadmap', 'subsection_id': 'development-roadmap', 'order': 1},
            {'title': '11.2 Team Structure', 'subsection_id': 'team-structure', 'order': 2},
            {'title': '11.3 Budget', 'subsection_id': 'budget', 'order': 3},
            {'title': '11.4 Post-Launch Support', 'subsection_id': 'post-launch-support', 'order': 4}
        ]
    },
    {
        'title': '12. Marketing & Distribution',
        'section_id': 'marketing',
        'order': 12,
        'subsections': [
            {'title': '12.1 Marketing Strategy', 'subsection_id': 'marketing-strategy', 'order': 1},
            {'title': '12.2 Promotional Channels', 'subsection_id': 'promotional-channels', 'order': 2},
            {'title': '12.3 Distribution Platforms', 'subsection_id': 'distribution-platforms', 'order': 3},
            {'title': '12.4 Community', 'subsection_id': 'community', 'order': 4}
        ]
    },
    {
        'title': '13. Appendices',
        'section_id': 'appendices',
        'order': 13,
        'subsections': [
            {'title': '13.1 Reference Materials', 'subsection_id': 'reference-materials', 'order': 1},
            {'title': '13.2 Technical Specifications', 'subsection_id': 'technical-specifications', 'order': 2},
            {'title': '13.3 Change Log', 'subsection_id': 'change-log', 'order': 3},
            {'title': '13.4 Glossary', 'subsection_id': 'glossary', 'order': 4}
        ]
    }
]
