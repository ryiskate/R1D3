from django import forms
from .game_models import (
    GameProject, GameDesignDocument, GameAsset, GameMilestone, 
    GameTask, GameBuild, PlaytestSession, PlaytestFeedback, GameBug
)


class GameProjectForm(forms.ModelForm):
    class Meta:
        model = GameProject
        fields = [
            'title', 'tagline', 'description', 'status', 'genre', 'platforms',
            'target_audience', 'start_date', 'target_release_date', 'budget',
            'lead_developer', 'lead_designer', 'lead_artist', 'team_members',
            # GitHub integration fields
            'github_repository', 'github_username', 'github_token', 'github_webhook_secret',
            'github_branch', 'auto_sync',
            # Other external links
            'trello_board', 'discord_channel',
            'logo', 'cover_image'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'target_audience': forms.TextInput(attrs={'placeholder': 'e.g., Casual gamers, 18-35 years old'}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'target_release_date': forms.DateInput(attrs={'type': 'date'}),
            'team_members': forms.SelectMultiple(attrs={'class': 'select2'}),
            # GitHub integration widgets
            'github_repository': forms.URLInput(attrs={'placeholder': 'https://github.com/username/repo'}),
            'github_username': forms.TextInput(attrs={'placeholder': 'username or organization'}),
            'github_token': forms.PasswordInput(attrs={'placeholder': 'Personal access token'}),
            'github_webhook_secret': forms.TextInput(attrs={'placeholder': 'Webhook secret (optional)'}),
            'github_branch': forms.TextInput(attrs={'placeholder': 'main'}),
            # Other external links
            'trello_board': forms.URLInput(attrs={'placeholder': 'https://trello.com/b/...'}),
            'discord_channel': forms.URLInput(attrs={'placeholder': 'https://discord.gg/...'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['github_token'].required = False
        self.fields['github_webhook_secret'].required = False


class GameDesignDocumentForm(forms.ModelForm):
    class Meta:
        model = GameDesignDocument
        fields = [
            'high_concept', 'player_experience', 'core_mechanics', 'game_rules',
            'controls', 'story_synopsis', 'world_building', 'art_style',
            'audio_style', 'technical_requirements', 'monetization', 'marketing'
        ]
        widgets = {
            'high_concept': forms.Textarea(attrs={'rows': 3, 'placeholder': 'One-paragraph summary of the game concept'}),
            'player_experience': forms.Textarea(attrs={'rows': 3, 'placeholder': 'What will the player experience?'}),
            'core_mechanics': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Key gameplay mechanics'}),
            'game_rules': forms.Textarea(attrs={'rows': 4}),
            'controls': forms.Textarea(attrs={'rows': 3}),
            'story_synopsis': forms.Textarea(attrs={'rows': 4}),
            'world_building': forms.Textarea(attrs={'rows': 4}),
            'art_style': forms.Textarea(attrs={'rows': 3}),
            'audio_style': forms.Textarea(attrs={'rows': 3}),
            'technical_requirements': forms.Textarea(attrs={'rows': 3}),
            'monetization': forms.Textarea(attrs={'rows': 3}),
            'marketing': forms.Textarea(attrs={'rows': 3}),
        }


class GameAssetForm(forms.ModelForm):
    class Meta:
        model = GameAsset
        fields = [
            'name', 'description', 'asset_type', 'status',
            'file', 'external_url', 'category', 'tags', 'assigned_to'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'external_url': forms.URLInput(attrs={'placeholder': 'https://...'}),
            'category': forms.TextInput(attrs={'placeholder': 'e.g., Characters, Environment, UI'}),
            'tags': forms.TextInput(attrs={'placeholder': 'e.g., player, enemy, level1'}),
        }


class GameMilestoneForm(forms.ModelForm):
    class Meta:
        model = GameMilestone
        fields = ['title', 'description', 'due_date', 'is_completed', 'completion_date']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'completion_date': forms.DateInput(attrs={'type': 'date'}),
        }


class GameTaskForm(forms.ModelForm):
    class Meta:
        model = GameTask
        fields = [
            'title', 'description', 'task_type', 'status', 'priority',
            'milestone', 'assigned_to', 'due_date', 'estimated_hours', 'actual_hours'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }


class GameBuildForm(forms.ModelForm):
    class Meta:
        model = GameBuild
        fields = [
            'version_number', 'version_type', 'build_date', 'notes',
            'build_file', 'download_url', 'platform', 'is_public'
        ]
        widgets = {
            'build_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'notes': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Release notes or changelog'}),
            'download_url': forms.URLInput(attrs={'placeholder': 'https://...'}),
        }


class PlaytestSessionForm(forms.ModelForm):
    class Meta:
        model = PlaytestSession
        fields = [
            'title', 'build', 'date', 'location', 'is_remote',
            'objectives', 'participants_count'
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'objectives': forms.Textarea(attrs={'rows': 3, 'placeholder': 'What are you trying to learn from this playtest?'}),
        }


class PlaytestFeedbackForm(forms.ModelForm):
    class Meta:
        model = PlaytestFeedback
        fields = [
            'tester_name', 'tester_email', 'tester_demographics',
            'overall_experience', 'gameplay_feedback', 'visual_feedback',
            'audio_feedback', 'narrative_feedback', 'technical_issues', 'suggestions'
        ]
        widgets = {
            'tester_demographics': forms.TextInput(attrs={'placeholder': 'Age, gaming experience, etc.'}),
            'gameplay_feedback': forms.Textarea(attrs={'rows': 3}),
            'visual_feedback': forms.Textarea(attrs={'rows': 3}),
            'audio_feedback': forms.Textarea(attrs={'rows': 3}),
            'narrative_feedback': forms.Textarea(attrs={'rows': 3}),
            'technical_issues': forms.Textarea(attrs={'rows': 3}),
            'suggestions': forms.Textarea(attrs={'rows': 3}),
        }


class GameBugForm(forms.ModelForm):
    class Meta:
        model = GameBug
        fields = [
            'title', 'description', 'steps_to_reproduce', 'expected_result',
            'actual_result', 'severity', 'status', 'assigned_to', 'screenshot'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'steps_to_reproduce': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Step-by-step instructions to reproduce the bug'}),
            'expected_result': forms.Textarea(attrs={'rows': 2}),
            'actual_result': forms.Textarea(attrs={'rows': 2}),
        }
