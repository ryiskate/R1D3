from django import forms
from .models import Profile, QuickLink

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['job_title', 'department', 'bio', 'profile_image']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
        }


class QuickLinkForm(forms.ModelForm):
    """Form for creating and editing quick links"""
    
    ICON_CHOICES = [
        ('fas fa-link', 'Link'),
        ('fas fa-home', 'Home'),
        ('fas fa-gamepad', 'Game'),
        ('fas fa-tasks', 'Tasks'),
        ('fas fa-clipboard-list', 'Clipboard'),
        ('fas fa-file-alt', 'Document'),
        ('fas fa-chart-bar', 'Chart'),
        ('fas fa-users', 'Users'),
        ('fas fa-cog', 'Settings'),
        ('fas fa-calendar', 'Calendar'),
        ('fas fa-envelope', 'Email'),
        ('fas fa-bell', 'Notification'),
        ('fas fa-star', 'Star'),
        ('fas fa-heart', 'Heart'),
        ('fas fa-bookmark', 'Bookmark'),
        ('fas fa-code', 'Code'),
        ('fas fa-database', 'Database'),
        ('fas fa-server', 'Server'),
        ('fas fa-desktop', 'Desktop'),
        ('fas fa-mobile-alt', 'Mobile'),
    ]
    
    icon = forms.ChoiceField(
        choices=ICON_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control icon-select'})
    )
    
    class Meta:
        model = QuickLink
        fields = ['name', 'url', 'icon']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Link Name'}),
            'url': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'URL or Path (e.g., /dashboard/ or https://example.com)'}),
        }
