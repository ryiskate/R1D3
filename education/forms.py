from django import forms
from django.forms import inlineformset_factory
from .models import (
    CourseDocumentation, 
    ConceptSection, 
    AdvancedTopicSection, 
    PracticalExample, 
    GlossaryTerm
)


class CourseDocumentationForm(forms.ModelForm):
    """Form for creating and editing course documentation"""
    
    class Meta:
        model = CourseDocumentation
        fields = [
            'title', 'central_theme', 'objective', 'summary', 
            'introduction', 'practical_applications', 
            'recommended_resources', 'attachments', 'status'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'central_theme': forms.TextInput(attrs={'class': 'form-control'}),
            'objective': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'summary': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'introduction': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'practical_applications': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'recommended_resources': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'attachments': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }


class ConceptSectionForm(forms.ModelForm):
    """Form for creating and editing concept sections"""
    
    class Meta:
        model = ConceptSection
        fields = ['name', 'definition', 'detailed_explanation', 'illustrative_example', 'order']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'definition': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'detailed_explanation': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'illustrative_example': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class AdvancedTopicSectionForm(forms.ModelForm):
    """Form for creating and editing advanced topic sections"""
    
    class Meta:
        model = AdvancedTopicSection
        fields = ['name', 'applications', 'challenges', 'real_example', 'order']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'applications': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'challenges': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'real_example': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class PracticalExampleForm(forms.ModelForm):
    """Form for creating and editing practical examples"""
    
    class Meta:
        model = PracticalExample
        fields = ['title', 'code', 'image', 'step_by_step', 'real_application', 'order']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'style': 'font-family: monospace;'}),
            'image': forms.URLInput(attrs={'class': 'form-control'}),
            'step_by_step': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'real_application': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class GlossaryTermForm(forms.ModelForm):
    """Form for creating and editing glossary terms"""
    
    class Meta:
        model = GlossaryTerm
        fields = ['term', 'definition']
        widgets = {
            'term': forms.TextInput(attrs={'class': 'form-control'}),
            'definition': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


# Create formsets for related models
ConceptSectionFormSet = inlineformset_factory(
    CourseDocumentation, 
    ConceptSection, 
    form=ConceptSectionForm,
    extra=1, 
    can_delete=True
)

AdvancedTopicSectionFormSet = inlineformset_factory(
    CourseDocumentation, 
    AdvancedTopicSection, 
    form=AdvancedTopicSectionForm,
    extra=1, 
    can_delete=True
)

PracticalExampleFormSet = inlineformset_factory(
    CourseDocumentation, 
    PracticalExample, 
    form=PracticalExampleForm,
    extra=1, 
    can_delete=True
)

GlossaryTermFormSet = inlineformset_factory(
    CourseDocumentation, 
    GlossaryTerm, 
    form=GlossaryTermForm,
    extra=3, 
    can_delete=True
)
