from django import forms
from django.contrib.auth import get_user_model
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, Div, HTML
from .models import IndieNewsTask, IndieGame, IndieEvent, IndieTool
from projects.models import Team

User = get_user_model()

class IndieNewsTaskForm(forms.ModelForm):
    """
    Form for creating and updating indie news tasks
    """
    class Meta:
        model = IndieNewsTask
        fields = [
            'title', 'description', 'status', 'priority', 
            'assigned_to', 'assigned_users', 'due_date', 'estimated_hours',
            'article_id', 'news_type', 'developer', 'game_title',
            'publish_date', 'word_count', 'tags'
        ]
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'publish_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
            'tags': forms.TextInput(attrs={'placeholder': 'Separate tags with commas'}),
            'assigned_users': forms.SelectMultiple(attrs={'class': 'select2', 'multiple': 'multiple'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set up the assigned_users field to show all users
        self.fields["assigned_users"].queryset = User.objects.all().order_by("username")
        self.fields["assigned_users"].label = "Team"
        self.fields["assigned_users"].help_text = "Hold Ctrl/Cmd to select multiple users"
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Fieldset(
                'Basic Information',
                'title',
                'description',
                Div(
                    Div('status', css_class='col-md-6'),
                    Div('priority', css_class='col-md-6'),
                    css_class='row'
                ),
                Div(
                    Div('assigned_to', css_class='col-md-6'),
                    Div('assigned_users', css_class='col-md-6'),
                    css_class='row'
                ),
                Div(
                    Div('due_date', css_class='col-md-12'),
                    css_class='row'
                ),
            ),
            Fieldset(
                'Article Details',
                Div(
                    Div('article_id', css_class='col-md-6'),
                    Div('news_type', css_class='col-md-6'),
                    css_class='row'
                ),
                Div(
                    Div('developer', css_class='col-md-6'),
                    Div('game_title', css_class='col-md-6'),
                    css_class='row'
                ),
                Div(
                    Div('publish_date', css_class='col-md-6'),
                    Div('word_count', css_class='col-md-6'),
                    css_class='row'
                ),
            ),
            Fieldset(
                'Additional Information',
                'estimated_hours',
                'tags',
            ),
            Div(
                Submit('submit', 'Save Task', css_class='btn btn-primary'),
                HTML('<a href="{% url \'indie_news:task_list\' %}" class="btn btn-secondary">Cancel</a>'),
                css_class='d-flex justify-content-between mt-4'
            )
        )


class IndieGameForm(forms.ModelForm):
    """
    Form for creating and updating indie games
    """
    class Meta:
        model = IndieGame
        fields = [
            'title', 'developer', 'publisher', 'release_date', 
            'description', 'platforms', 'genres', 'price',
            'website', 'steam_url', 'itch_url', 'cover_image',
            'trailer_url', 'review_score', 'review_url'
        ]
        widgets = {
            'release_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
            'platforms': forms.SelectMultiple(attrs={'class': 'select2'}),
            'genres': forms.SelectMultiple(attrs={'class': 'select2'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_enctype = 'multipart/form-data'
        self.helper.layout = Layout(
            Fieldset(
                'Game Information',
                'title',
                'description',
                Div(
                    Div('developer', css_class='col-md-6'),
                    Div('publisher', css_class='col-md-6'),
                    css_class='row'
                ),
                Div(
                    Div('release_date', css_class='col-md-6'),
                    Div('price', css_class='col-md-6'),
                    css_class='row'
                ),
            ),
            Fieldset(
                'Game Details',
                Div(
                    Div('platforms', css_class='col-md-6'),
                    Div('genres', css_class='col-md-6'),
                    css_class='row'
                ),
            ),
            Fieldset(
                'Links & Media',
                Div(
                    Div('website', css_class='col-md-6'),
                    Div('trailer_url', css_class='col-md-6'),
                    css_class='row'
                ),
                Div(
                    Div('steam_url', css_class='col-md-6'),
                    Div('itch_url', css_class='col-md-6'),
                    css_class='row'
                ),
                'cover_image',
            ),
            Fieldset(
                'Review Information',
                Div(
                    Div('review_score', css_class='col-md-6'),
                    Div('review_url', css_class='col-md-6'),
                    css_class='row'
                ),
            ),
            Div(
                Submit('submit', 'Save Game', css_class='btn btn-primary'),
                HTML('<a href="{% url \'indie_news:game_list\' %}" class="btn btn-secondary">Cancel</a>'),
                css_class='d-flex justify-content-between mt-4'
            )
        )


class IndieEventForm(forms.ModelForm):
    """
    Form for creating and updating indie events
    """
    class Meta:
        model = IndieEvent
        fields = [
            'name', 'description', 'start_date', 'end_date', 
            'location', 'website', 'event_type', 'is_virtual',
            'is_free', 'ticket_url', 'is_covered', 'coverage_url'
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Fieldset(
                'Event Information',
                'name',
                'description',
                Div(
                    Div('start_date', css_class='col-md-6'),
                    Div('end_date', css_class='col-md-6'),
                    css_class='row'
                ),
                Div(
                    Div('location', css_class='col-md-6'),
                    Div('event_type', css_class='col-md-6'),
                    css_class='row'
                ),
            ),
            Fieldset(
                'Event Details',
                Div(
                    Div('is_virtual', css_class='col-md-6'),
                    Div('is_free', css_class='col-md-6'),
                    css_class='row'
                ),
                Div(
                    Div('website', css_class='col-md-6'),
                    Div('ticket_url', css_class='col-md-6'),
                    css_class='row'
                ),
            ),
            Fieldset(
                'Coverage Information',
                Div(
                    Div('is_covered', css_class='col-md-6'),
                    Div('coverage_url', css_class='col-md-6'),
                    css_class='row'
                ),
            ),
            Div(
                Submit('submit', 'Save Event', css_class='btn btn-primary'),
                HTML('<a href="{% url \'indie_news:event_list\' %}" class="btn btn-secondary">Cancel</a>'),
                css_class='d-flex justify-content-between mt-4'
            )
        )


class IndieToolForm(forms.ModelForm):
    """
    Form for creating and updating indie development tools
    """
    class Meta:
        model = IndieTool
        fields = [
            'name', 'description', 'website', 'tool_type', 
            'pricing_model', 'price', 'windows_support',
            'mac_support', 'linux_support', 'has_review', 'review_url'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Fieldset(
                'Tool Information',
                'name',
                'description',
                Div(
                    Div('website', css_class='col-md-6'),
                    Div('tool_type', css_class='col-md-6'),
                    css_class='row'
                ),
            ),
            Fieldset(
                'Pricing Details',
                Div(
                    Div('pricing_model', css_class='col-md-6'),
                    Div('price', css_class='col-md-6'),
                    css_class='row'
                ),
            ),
            Fieldset(
                'Platform Support',
                Div(
                    Div('windows_support', css_class='col-md-4'),
                    Div('mac_support', css_class='col-md-4'),
                    Div('linux_support', css_class='col-md-4'),
                    css_class='row'
                ),
            ),
            Fieldset(
                'Review Information',
                Div(
                    Div('has_review', css_class='col-md-6'),
                    Div('review_url', css_class='col-md-6'),
                    css_class='row'
                ),
            ),
            Div(
                Submit('submit', 'Save Tool', css_class='btn btn-primary'),
                HTML('<a href="{% url \'indie_news:tool_list\' %}" class="btn btn-secondary">Cancel</a>'),
                css_class='d-flex justify-content-between mt-4'
            )
        )
