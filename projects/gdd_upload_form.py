from django import forms
from django.core.validators import FileExtensionValidator

class GDDUploadForm(forms.Form):
    """
    Form for uploading a GDD HTML file
    """
    gdd_file = forms.FileField(
        label='Upload Game Design Document',
        help_text='Upload an HTML file containing your Game Design Document',
        validators=[FileExtensionValidator(allowed_extensions=['html', 'htm'])]
    )
    auto_create_tasks = forms.BooleanField(
        label='Automatically create tasks for features',
        help_text='Create tasks for features that don\'t already exist',
        required=False,
        initial=True
    )
    update_existing = forms.BooleanField(
        label='Update existing GDD',
        help_text='If a GDD already exists, update it with the uploaded content',
        required=False,
        initial=True
    )
