from django.db import models
from django.contrib.auth.models import User
from core.models import TimeStampedModel
from strategy.models import Goal, Objective


class GameProject(TimeStampedModel):
    """
    Game Project model for managing game development projects
    """
    STATUS_CHOICES = [
        ('concept', 'Concept'),
        ('pre_production', 'Pre-Production'),
        ('production', 'Production'),
        ('alpha', 'Alpha'),
        ('beta', 'Beta'),
        ('release', 'Released'),
        ('post_release', 'Post-Release Support'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    PLATFORM_CHOICES = [
        ('pc', 'PC'),
        ('mobile', 'Mobile'),
        ('console', 'Console'),
        ('web', 'Web'),
        ('vr', 'Virtual Reality'),
        ('ar', 'Augmented Reality'),
        ('multi', 'Multi-platform'),
    ]
    
    GENRE_CHOICES = [
        ('action', 'Action'),
        ('adventure', 'Adventure'),
        ('rpg', 'Role-Playing Game'),
        ('strategy', 'Strategy'),
        ('simulation', 'Simulation'),
        ('sports', 'Sports'),
        ('puzzle', 'Puzzle'),
        ('shooter', 'Shooter'),
        ('platformer', 'Platformer'),
        ('racing', 'Racing'),
        ('mmo', 'MMO'),
        ('other', 'Other'),
    ]
    
    # Basic information
    title = models.CharField(max_length=200)
    tagline = models.CharField(max_length=200, blank=True, help_text="Short description/slogan for the game")
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='concept')
    
    # Game details
    genre = models.CharField(max_length=20, choices=GENRE_CHOICES, default='other')
    platforms = models.CharField(max_length=20, choices=PLATFORM_CHOICES, default='pc')
    target_audience = models.CharField(max_length=200, blank=True)
    
    # Project management
    start_date = models.DateField()
    target_release_date = models.DateField(null=True, blank=True)
    actual_release_date = models.DateField(null=True, blank=True)
    budget = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    # Team
    lead_developer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='led_games')
    lead_designer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='designed_games')
    lead_artist = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='art_directed_games')
    team_members = models.ManyToManyField(User, related_name='game_projects', blank=True)
    
    # GitHub Integration
    github_repository = models.URLField(blank=True, help_text="URL to the GitHub repository")
    github_username = models.CharField(max_length=100, blank=True, help_text="GitHub username or organization")
    github_token = models.CharField(max_length=100, blank=True, help_text="GitHub personal access token (stored securely)")
    github_webhook_secret = models.CharField(max_length=100, blank=True, help_text="Secret for GitHub webhooks")
    github_branch = models.CharField(max_length=100, default="main", help_text="Default branch to track")
    auto_sync = models.BooleanField(default=False, help_text="Automatically sync with GitHub repository")
    
    # External links
    trello_board = models.URLField(blank=True, help_text="URL to Trello board if used")
    discord_channel = models.URLField(blank=True, help_text="URL to Discord channel")
    
    # Media
    logo = models.ImageField(upload_to='game_logos/', null=True, blank=True)
    cover_image = models.ImageField(upload_to='game_covers/', null=True, blank=True)
    
    # Strategic alignment
    related_goals = models.ManyToManyField(Goal, related_name='game_projects', blank=True)
    related_objectives = models.ManyToManyField(Objective, related_name='game_projects', blank=True)
    
    def __str__(self):
        return self.title
    
    @property
    def is_active(self):
        return self.status in ['pre_production', 'production', 'alpha', 'beta']
    
    @property
    def is_released(self):
        return self.status in ['release', 'post_release', 'completed']


class GameDesignDocument(TimeStampedModel):
    """
    Game Design Document (GDD) for a game project
    """
    game = models.OneToOneField(GameProject, on_delete=models.CASCADE, related_name='design_document')
    
    # Core concept
    high_concept = models.TextField(help_text="One-paragraph summary of the game")
    player_experience = models.TextField(help_text="What the player will experience")
    
    # Gameplay
    core_mechanics = models.TextField(help_text="Core gameplay mechanics")
    game_rules = models.TextField(blank=True, help_text="Rules of the game")
    controls = models.TextField(blank=True, help_text="Player controls")
    
    # Narrative
    story_synopsis = models.TextField(blank=True, help_text="Synopsis of the game's story")
    world_building = models.TextField(blank=True, help_text="Description of the game world")
    
    # Art and audio
    art_style = models.TextField(blank=True, help_text="Description of the visual style")
    audio_style = models.TextField(blank=True, help_text="Description of music and sound design")
    
    # Technical
    technical_requirements = models.TextField(blank=True, help_text="Technical specifications and requirements")
    
    # Business
    monetization = models.TextField(blank=True, help_text="Monetization strategy")
    marketing = models.TextField(blank=True, help_text="Marketing strategy")
    
    def __str__(self):
        return f"GDD for {self.game.title}"


class GameAsset(TimeStampedModel):
    """
    Game asset (art, audio, code, etc.)
    """
    ASSET_TYPE_CHOICES = [
        ('2d_art', '2D Art'),
        ('3d_model', '3D Model'),
        ('animation', 'Animation'),
        ('texture', 'Texture'),
        ('sound', 'Sound Effect'),
        ('music', 'Music'),
        ('voice', 'Voice Acting'),
        ('code', 'Code'),
        ('document', 'Document'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('review', 'In Review'),
        ('approved', 'Approved'),
        ('implemented', 'Implemented'),
        ('rejected', 'Rejected'),
    ]
    
    game = models.ForeignKey(GameProject, on_delete=models.CASCADE, related_name='assets')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    asset_type = models.CharField(max_length=20, choices=ASSET_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planned')
    
    # File management
    file = models.FileField(upload_to='game_assets/', null=True, blank=True)
    external_url = models.URLField(blank=True, help_text="URL to external storage if not uploaded directly")
    
    # Organization
    category = models.CharField(max_length=100, blank=True, help_text="Custom category for organization")
    tags = models.CharField(max_length=200, blank=True, help_text="Comma-separated tags")
    
    # Ownership
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_assets')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_assets')
    
    def __str__(self):
        return f"{self.name} ({self.get_asset_type_display()})"


class GameMilestone(TimeStampedModel):
    """
    Game development milestone
    """
    game = models.ForeignKey(GameProject, on_delete=models.CASCADE, related_name='milestones')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    due_date = models.DateField()
    is_completed = models.BooleanField(default=False)
    completion_date = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.game.title} - {self.title}"


class GameTask(TimeStampedModel):
    """
    Game development task
    """
    STATUS_CHOICES = [
        ('backlog', 'Backlog'),
        ('to_do', 'To Do'),
        ('in_progress', 'In Progress'),
        ('in_review', 'In Review'),
        ('done', 'Done'),
        ('blocked', 'Blocked'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    TASK_TYPE_CHOICES = [
        ('design', 'Game Design'),
        ('art', 'Art'),
        ('programming', 'Programming'),
        ('audio', 'Audio'),
        ('testing', 'Testing'),
        ('writing', 'Writing'),
        ('other', 'Other'),
    ]
    
    game = models.ForeignKey(GameProject, on_delete=models.CASCADE, related_name='tasks')
    milestone = models.ForeignKey(GameMilestone, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    task_type = models.CharField(max_length=20, choices=TASK_TYPE_CHOICES, default='other')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='backlog')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='game_tasks')
    due_date = models.DateField(null=True, blank=True)
    estimated_hours = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    actual_hours = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    
    def __str__(self):
        return self.title


class GameBuild(TimeStampedModel):
    """
    Game build/version for tracking releases
    """
    VERSION_TYPE_CHOICES = [
        ('internal', 'Internal'),
        ('alpha', 'Alpha'),
        ('beta', 'Beta'),
        ('release_candidate', 'Release Candidate'),
        ('release', 'Release'),
        ('patch', 'Patch'),
    ]
    
    game = models.ForeignKey(GameProject, on_delete=models.CASCADE, related_name='builds')
    version_number = models.CharField(max_length=50, help_text="e.g., 0.1.0, 1.0.0")
    version_type = models.CharField(max_length=20, choices=VERSION_TYPE_CHOICES)
    build_date = models.DateTimeField()
    notes = models.TextField(blank=True, help_text="Release notes or changelog")
    
    # Build files
    build_file = models.FileField(upload_to='game_builds/', null=True, blank=True)
    download_url = models.URLField(blank=True, help_text="External download URL if not hosted directly")
    
    # Build info
    platform = models.CharField(max_length=50, help_text="Platform this build is for")
    is_public = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.game.title} v{self.version_number} ({self.get_version_type_display()})"


class PlaytestSession(TimeStampedModel):
    """
    Playtest session for gathering feedback
    """
    game = models.ForeignKey(GameProject, on_delete=models.CASCADE, related_name='playtest_sessions')
    build = models.ForeignKey(GameBuild, on_delete=models.SET_NULL, null=True, related_name='playtest_sessions')
    title = models.CharField(max_length=200)
    date = models.DateField()
    location = models.CharField(max_length=200, blank=True)
    is_remote = models.BooleanField(default=False)
    objectives = models.TextField(help_text="What are you trying to learn from this playtest?")
    participants_count = models.IntegerField(default=0)
    summary = models.TextField(blank=True, help_text="Summary of findings")
    
    def __str__(self):
        return f"{self.game.title} - {self.title}"


class PlaytestFeedback(TimeStampedModel):
    """
    Individual feedback from playtesting
    """
    SENTIMENT_CHOICES = [
        ('very_negative', 'Very Negative'),
        ('negative', 'Negative'),
        ('neutral', 'Neutral'),
        ('positive', 'Positive'),
        ('very_positive', 'Very Positive'),
    ]
    
    session = models.ForeignKey(PlaytestSession, on_delete=models.CASCADE, related_name='feedback')
    tester_name = models.CharField(max_length=100, blank=True)
    tester_email = models.EmailField(blank=True)
    tester_demographics = models.CharField(max_length=200, blank=True, help_text="Age, gaming experience, etc.")
    
    # Feedback
    overall_experience = models.CharField(max_length=20, choices=SENTIMENT_CHOICES, default='neutral')
    gameplay_feedback = models.TextField(blank=True)
    visual_feedback = models.TextField(blank=True)
    audio_feedback = models.TextField(blank=True)
    narrative_feedback = models.TextField(blank=True)
    technical_issues = models.TextField(blank=True)
    suggestions = models.TextField(blank=True)
    
    def __str__(self):
        return f"Feedback from {self.tester_name or 'Anonymous'} - {self.session.title}"


class GameBug(TimeStampedModel):
    """
    Bug tracking for game development
    """
    SEVERITY_CHOICES = [
        ('trivial', 'Trivial'),
        ('minor', 'Minor'),
        ('major', 'Major'),
        ('critical', 'Critical'),
        ('blocker', 'Blocker'),
    ]
    
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('fixed', 'Fixed'),
        ('verified', 'Verified'),
        ('closed', 'Closed'),
        ('wont_fix', 'Won\'t Fix'),
    ]
    
    game = models.ForeignKey(GameProject, on_delete=models.CASCADE, related_name='bugs')
    build = models.ForeignKey(GameBuild, on_delete=models.SET_NULL, null=True, blank=True, related_name='bugs')
    title = models.CharField(max_length=200)
    description = models.TextField()
    steps_to_reproduce = models.TextField()
    expected_result = models.TextField()
    actual_result = models.TextField()
    
    # Classification
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='minor')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    
    # Assignment
    reported_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='reported_bugs')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_bugs')
    
    # Media
    screenshot = models.ImageField(upload_to='bug_screenshots/', null=True, blank=True)
    
    def __str__(self):
        return f"{self.game.title} - {self.title}"
