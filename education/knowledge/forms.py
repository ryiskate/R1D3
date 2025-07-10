from django import forms
from django.utils.text import slugify
from .models import KnowledgeArticle, KnowledgeCategory, KnowledgeTag, MediaAttachment


class KnowledgeArticleForm(forms.ModelForm):
    """Form for creating and updating knowledge articles"""
    
    class Meta:
        model = KnowledgeArticle
        fields = [
            'title', 'slug', 'summary', 'content', 'category', 
            'tags', 'featured_image', 'is_published'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'summary': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'content': forms.Textarea(attrs={'class': 'form-control tinymce', 'rows': 20}),
            'category': forms.Select(attrs={'class': 'form-control select2'}),
            'tags': forms.SelectMultiple(attrs={'class': 'form-control select2'}),
            'featured_image': forms.FileInput(attrs={'class': 'form-control'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['slug'].required = False
        self.fields['slug'].help_text = "Leave blank to auto-generate from title"
        
        # Add "Create new" options for category and tags
        self.fields['category'].empty_label = "Select a category"
        
        # Make tags more user-friendly
        self.fields['tags'].help_text = "Hold Ctrl (or Cmd on Mac) to select multiple tags"
    
    def clean_slug(self):
        slug = self.cleaned_data.get('slug')
        title = self.cleaned_data.get('title')
        
        # If slug is not provided, generate from title
        if not slug and title:
            slug = slugify(title)
        
        # Check if slug exists for another article
        if slug:
            instance = self.instance
            qs = KnowledgeArticle.objects.filter(slug=slug)
            if instance and instance.pk:
                qs = qs.exclude(pk=instance.pk)
            if qs.exists():
                raise forms.ValidationError("This slug is already in use. Please choose a different one.")
        
        return slug


class MediaAttachmentForm(forms.ModelForm):
    """Form for uploading media attachments"""
    
    class Meta:
        model = MediaAttachment
        fields = ['file', 'file_type', 'title', 'description']
        widgets = {
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'file_type': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class KnowledgeCategoryForm(forms.ModelForm):
    """Form for creating and updating knowledge categories"""
    
    class Meta:
        model = KnowledgeCategory
        fields = ['name', 'slug', 'description', 'icon', 'color', 'order']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'icon': forms.TextInput(attrs={'class': 'form-control'}),
            'color': forms.TextInput(attrs={'class': 'form-control color-picker'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['slug'].required = False
        self.fields['slug'].help_text = "Leave blank to auto-generate from name"
    
    def clean_slug(self):
        slug = self.cleaned_data.get('slug')
        name = self.cleaned_data.get('name')
        
        # If slug is not provided, generate from name
        if not slug and name:
            slug = slugify(name)
        
        # Check if slug exists for another category
        if slug:
            instance = self.instance
            qs = KnowledgeCategory.objects.filter(slug=slug)
            if instance and instance.pk:
                qs = qs.exclude(pk=instance.pk)
            if qs.exists():
                raise forms.ValidationError("This slug is already in use. Please choose a different one.")
        
        return slug


class KnowledgeTagForm(forms.ModelForm):
    """Form for creating and updating knowledge tags"""
    
    class Meta:
        model = KnowledgeTag
        fields = ['name', 'slug']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['slug'].required = False
        self.fields['slug'].help_text = "Leave blank to auto-generate from name"
    
    def clean_slug(self):
        slug = self.cleaned_data.get('slug')
        name = self.cleaned_data.get('name')
        
        # If slug is not provided, generate from name
        if not slug and name:
            slug = slugify(name)
        
        # Check if slug exists for another tag
        if slug:
            instance = self.instance
            qs = KnowledgeTag.objects.filter(slug=slug)
            if instance and instance.pk:
                qs = qs.exclude(pk=instance.pk)
            if qs.exists():
                raise forms.ValidationError("This slug is already in use. Please choose a different one.")
        
        return slug
