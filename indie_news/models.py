from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from projects.task_models import BaseTask

User = get_user_model()

class IndieNewsTask(BaseTask):
    """
    Tasks specific to indie news management
    """
    # Indie news specific fields
    article_id = models.CharField(max_length=100, blank=True)
    news_type = models.CharField(max_length=100, blank=True, 
                                choices=[
                                    ('review', 'Game Review'),
                                    ('preview', 'Game Preview'),
                                    ('interview', 'Developer Interview'),
                                    ('feature', 'Feature Article'),
                                    ('news', 'News Article'),
                                    ('opinion', 'Opinion Piece'),
                                    ('guide', 'Game Guide'),
                                ])
    developer = models.CharField(max_length=255, blank=True)
    game_title = models.CharField(max_length=255, blank=True)
    publish_date = models.DateField(null=True, blank=True)
    word_count = models.IntegerField(default=0)
    
    # Multiple users can be assigned to a task
    assigned_users = models.ManyToManyField(User, related_name='assigned_indie_news_tasks', blank=True)
    
    class Meta:
        verbose_name = "Indie News Task"
        verbose_name_plural = "Indie News Tasks"


class IndieGame(models.Model):
    """
    Model for tracking indie games covered by the news section
    """
    title = models.CharField(max_length=255)
    developer = models.CharField(max_length=255)
    publisher = models.CharField(max_length=255, blank=True)
    release_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)
    
    # Game details
    PLATFORM_CHOICES = [
        ('pc', 'PC'),
        ('mac', 'Mac'),
        ('linux', 'Linux'),
        ('switch', 'Nintendo Switch'),
        ('ps4', 'PlayStation 4'),
        ('ps5', 'PlayStation 5'),
        ('xbox_one', 'Xbox One'),
        ('xbox_series', 'Xbox Series X/S'),
        ('mobile', 'Mobile'),
        ('web', 'Web Browser'),
        ('other', 'Other'),
    ]
    
    GENRE_CHOICES = [
        ('action', 'Action'),
        ('adventure', 'Adventure'),
        ('rpg', 'RPG'),
        ('strategy', 'Strategy'),
        ('simulation', 'Simulation'),
        ('puzzle', 'Puzzle'),
        ('platformer', 'Platformer'),
        ('racing', 'Racing'),
        ('sports', 'Sports'),
        ('horror', 'Horror'),
        ('shooter', 'Shooter'),
        ('other', 'Other'),
    ]
    
    platforms = models.CharField(max_length=255)
    genres = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    website = models.URLField(blank=True)
    steam_url = models.URLField(blank=True)
    itch_url = models.URLField(blank=True)
    
    # Media
    cover_image = models.ImageField(upload_to='indie_games/covers/', blank=True, null=True)
    trailer_url = models.URLField(blank=True)
    
    # Tracking
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='added_games')
    added_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    
    # Review information
    review_score = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    review_url = models.URLField(blank=True)
    
    def __str__(self):
        return f"{self.title} by {self.developer}"
    
    class Meta:
        ordering = ['-release_date', 'title']
        verbose_name = "Indie Game"
        verbose_name_plural = "Indie Games"


class IndieEvent(models.Model):
    """
    Model for tracking indie game events and conferences
    """
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    location = models.CharField(max_length=255)
    website = models.URLField(blank=True)
    
    # Event details
    EVENT_TYPE_CHOICES = [
        ('conference', 'Conference'),
        ('showcase', 'Game Showcase'),
        ('competition', 'Competition'),
        ('awards', 'Awards Ceremony'),
        ('meetup', 'Developer Meetup'),
        ('jam', 'Game Jam'),
        ('expo', 'Expo/Convention'),
        ('other', 'Other'),
    ]
    
    event_type = models.CharField(max_length=50, choices=EVENT_TYPE_CHOICES)
    is_virtual = models.BooleanField(default=False)
    is_free = models.BooleanField(default=False)
    ticket_url = models.URLField(blank=True)
    
    # Tracking
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='added_events')
    added_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    
    # Coverage
    is_covered = models.BooleanField(default=False)
    coverage_url = models.URLField(blank=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['start_date', 'name']
        verbose_name = "Indie Event"
        verbose_name_plural = "Indie Events"


class IndieTool(models.Model):
    """
    Model for tracking game development tools for indie developers
    """
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    website = models.URLField()
    
    # Tool details
    TOOL_TYPE_CHOICES = [
        ('engine', 'Game Engine'),
        ('graphics', 'Graphics Tool'),
        ('audio', 'Audio Tool'),
        ('modeling', '3D Modeling'),
        ('animation', 'Animation Tool'),
        ('ide', 'Development Environment'),
        ('framework', 'Framework/Library'),
        ('asset', 'Asset Store/Pack'),
        ('productivity', 'Productivity Tool'),
        ('other', 'Other'),
    ]
    
    PRICING_MODEL_CHOICES = [
        ('free', 'Free'),
        ('freemium', 'Freemium'),
        ('subscription', 'Subscription'),
        ('one_time', 'One-time Purchase'),
        ('open_source', 'Open Source'),
    ]
    
    tool_type = models.CharField(max_length=50, choices=TOOL_TYPE_CHOICES)
    pricing_model = models.CharField(max_length=50, choices=PRICING_MODEL_CHOICES)
    price = models.CharField(max_length=100, blank=True)
    
    # Platform compatibility
    windows_support = models.BooleanField(default=True)
    mac_support = models.BooleanField(default=False)
    linux_support = models.BooleanField(default=False)
    
    # Tracking
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='added_tools')
    added_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    
    # Review information
    has_review = models.BooleanField(default=False)
    review_url = models.URLField(blank=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']
        verbose_name = "Indie Tool"
        verbose_name_plural = "Indie Tools"
