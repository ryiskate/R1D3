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
    
    # HTML Content
    html_content = models.TextField(blank=True, help_text="Full HTML content of the GDD")
    use_html_content = models.BooleanField(default=False, help_text="Use HTML content instead of structured fields")
    
    def __str__(self):
        return f"GDD for {self.game.title}"


class GDDSection(TimeStampedModel):
    """
    A section of the Game Design Document that can be linked to tasks
    """
    gdd = models.ForeignKey(GameDesignDocument, on_delete=models.CASCADE, related_name='sections')
    title = models.CharField(max_length=100)
    content = models.TextField(blank=True)
    html_content = models.TextField(blank=True)
    section_id = models.CharField(max_length=50, help_text="Unique identifier for this section in the HTML document")
    order = models.PositiveIntegerField(default=0, help_text="Order of this section in the document")
    
    def __str__(self):
        return f"{self.title} - {self.gdd.game.title}"
    
    class Meta:
        ordering = ['order']


class GDDFeature(TimeStampedModel):
    """
    A feature from a GDD section's feature table that can be linked to tasks
    """
    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    )
    
    section = models.ForeignKey(GDDSection, on_delete=models.CASCADE, related_name='features')
    subsection_id = models.CharField(max_length=50, blank=True, null=True, help_text="ID of the subsection this feature belongs to")
    feature_name = models.CharField(max_length=100)
    description = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    # Use db_column to specify a different column name in the database
    # This avoids conflict with the status property method
    status = models.CharField(max_length=20, default='backlog', 
                            db_column='status_value',  # Use a different column name in the database
                            choices=(
                                ('backlog', 'Backlog'),
                                ('to_do', 'To Do'),
                                ('in_progress', 'In Progress'),
                                ('in_review', 'In Review'),
                                ('done', 'Done'),
                            ))
    notes = models.TextField(blank=True, null=True, help_text="Additional notes about this feature")
    task = models.OneToOneField('GameTask', on_delete=models.SET_NULL, null=True, blank=True, related_name='gdd_feature')
    order = models.PositiveIntegerField(default=0, help_text="Order of this feature within its section/subsection")
    
    def save(self, *args, **kwargs):
        # If order is not set, set it to the next available order number
        if self.order is None or self.order == 0:
            # Get the highest order number for features in this section and subsection
            if self.subsection_id:
                max_order = GDDFeature.objects.filter(
                    section=self.section,
                    subsection_id=self.subsection_id
                ).aggregate(models.Max('order'))['order__max'] or 0
            else:
                max_order = GDDFeature.objects.filter(
                    section=self.section,
                    subsection_id__isnull=True
                ).aggregate(models.Max('order'))['order__max'] or 0
            
            # Set order to one more than the highest existing order
            self.order = max_order + 1
        
        # Temporarily remove the status attribute to prevent database error
        # since the status column doesn't exist in the database table
        status_value = None
        if hasattr(self, '_status'):
            status_value = self._status
            delattr(self, '_status')
        
        # Call the parent save method
        super().save(*args, **kwargs)
        
        # Restore the status attribute if it was set
        if status_value is not None:
            self._status = status_value
    
    def __str__(self):
        return f"{self.feature_name} - {self.section.title}"
    
    @property
    def task_status(self):
        """Return the status of the linked task, or 'Planned' if no task is linked"""
        if self.task:
            return self.task.get_status_display()
        return "Planned"
    
    class Meta:
        ordering = ['order', 'priority', 'feature_name']


class GameAsset(TimeStampedModel):
    """
    Game asset (art, audio, code, etc.)
    """
    ASSET_TYPE_CHOICES = [
        ('3d_model', '3D Model'),
        ('2d_image', '2D Image'),
        ('music', 'Music'),
        ('video', 'Video'),
        ('reference', 'Reference'),
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
    thumbnail = models.ImageField(upload_to='game_assets/thumbnails/', null=True, blank=True, help_text="Custom thumbnail image for this asset")
    external_url = models.URLField(blank=True, help_text="URL to external storage if not uploaded directly")
    
    # Organization
    subtype = models.CharField(max_length=100, blank=True, help_text="Subtype of the asset (e.g., character, environment, concept art)")
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
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    
    game = models.ForeignKey(GameProject, on_delete=models.CASCADE, related_name='milestones')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    due_date = models.DateField()
    completion_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')
    
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
    
    COMPANY_SECTION_CHOICES = [
        ('game_development', 'Game Development'),
        ('education', 'Education'),
        ('arcade', 'Arcade'),
        ('marketing', 'Marketing'),
        ('finance', 'Finance'),
        ('hr', 'Human Resources'),
        ('it', 'IT & Infrastructure'),
        ('research', 'Research & Development'),
        ('other', 'Other'),
    ]
    
    game = models.ForeignKey(GameProject, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Associated Game', help_text='Required for game development tasks, leave empty for other sections')
    milestone = models.ForeignKey(GameMilestone, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    task_type = models.CharField(max_length=20, choices=TASK_TYPE_CHOICES, default='other')
    custom_type = models.CharField(max_length=100, blank=True, null=True, help_text="Custom task type when task_type is 'other'")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='backlog')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='game_tasks')
    due_date = models.DateField(null=True, blank=True)
    estimated_hours = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    actual_hours = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    company_section = models.CharField(max_length=30, choices=COMPANY_SECTION_CHOICES, default='game_development', help_text="Company section this task belongs to")
    
    # Game Development specific fields
    gdd_section = models.ForeignKey(GDDSection, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks', help_text="GDD section this task is related to")
    feature_id = models.CharField(max_length=50, null=True, blank=True, help_text="ID of the feature in the GDD")
    platform = models.CharField(max_length=50, null=True, blank=True, help_text="Platform this task is for (PC, mobile, console, etc.)")
    
    # Education specific fields
    course_id = models.CharField(max_length=50, null=True, blank=True, help_text="Course ID this task is related to")
    learning_objective = models.TextField(null=True, blank=True, help_text="Learning objective this task addresses")
    target_audience = models.CharField(max_length=100, null=True, blank=True, help_text="Target audience for this educational task")
    
    # Arcade specific fields
    machine_id = models.CharField(max_length=50, null=True, blank=True, help_text="Arcade machine ID this task is for")
    location = models.CharField(max_length=100, null=True, blank=True, help_text="Location of the arcade machine")
    maintenance_type = models.CharField(max_length=50, null=True, blank=True, help_text="Type of maintenance (repair, upgrade, cleaning, etc.)")
    
    # Marketing specific fields
    campaign_id = models.CharField(max_length=50, null=True, blank=True, help_text="Marketing campaign ID this task is part of")
    channel = models.CharField(max_length=50, null=True, blank=True, help_text="Marketing channel (social media, email, events, etc.)")
    target_metrics = models.TextField(null=True, blank=True, help_text="Target metrics for this marketing task")
    
    # Research & Development specific fields
    research_area = models.CharField(max_length=100, null=True, blank=True, help_text="Area of research this task is related to")
    experiment_id = models.CharField(max_length=50, null=True, blank=True, help_text="ID of the experiment this task is part of")
    hypothesis = models.TextField(null=True, blank=True, help_text="Hypothesis being tested in this research task")
    
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
