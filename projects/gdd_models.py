from django.db import models
from .game_models import GameProject, TimeStampedModel

class GameDesignDocumentType(models.Model):
    """
    Type of Game Design Document (e.g., Concept, Full, Technical, Art Bible)
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name

class MultiGDD(TimeStampedModel):
    """
    Game Design Document (GDD) for a game project
    This model allows multiple GDDs per game
    """
    game = models.ForeignKey(GameProject, on_delete=models.CASCADE, related_name='design_documents')
    title = models.CharField(max_length=200)
    version = models.CharField(max_length=20, default="1.0")
    gdd_type = models.ForeignKey(GameDesignDocumentType, on_delete=models.SET_NULL, null=True, blank=True, related_name='documents')
    
    # HTML Content
    html_content = models.TextField(blank=True, help_text="Full HTML content of the GDD")
    use_html_content = models.BooleanField(default=True, help_text="Use HTML content instead of structured fields")
    
    # Structured fields (optional)
    high_concept = models.TextField(blank=True, help_text="One-paragraph summary of the game")
    player_experience = models.TextField(blank=True, help_text="What the player will experience")
    core_mechanics = models.TextField(blank=True, help_text="Core gameplay mechanics")
    game_rules = models.TextField(blank=True, help_text="Rules of the game")
    controls = models.TextField(blank=True, help_text="Player controls")
    story_synopsis = models.TextField(blank=True, help_text="Synopsis of the game's story")
    world_building = models.TextField(blank=True, help_text="Description of the game world")
    art_style = models.TextField(blank=True, help_text="Description of the visual style")
    audio_style = models.TextField(blank=True, help_text="Description of music and sound design")
    technical_requirements = models.TextField(blank=True, help_text="Technical specifications and requirements")
    monetization = models.TextField(blank=True, help_text="Monetization strategy")
    marketing = models.TextField(blank=True, help_text="Marketing strategy")
    
    # Status and metadata
    is_active = models.BooleanField(default=True, help_text="Whether this is the active version of the GDD")
    is_published = models.BooleanField(default=False, help_text="Whether this GDD is published and viewable by team members")
    
    def __str__(self):
        return f"{self.title} v{self.version} - {self.game.title}"
    
    class Meta:
        ordering = ['-created']
        verbose_name = "Game Design Document"
        verbose_name_plural = "Game Design Documents"

class GDDSection(TimeStampedModel):
    """
    A section of the Game Design Document that can be linked to tasks
    """
    gdd = models.ForeignKey(MultiGDD, on_delete=models.CASCADE, related_name='sections')
    title = models.CharField(max_length=100)
    content = models.TextField(blank=True)
    html_content = models.TextField(blank=True)
    section_id = models.CharField(max_length=50, help_text="Unique identifier for this section in the HTML document")
    order = models.PositiveIntegerField(default=0, help_text="Order of this section in the document")
    
    def __str__(self):
        return f"{self.title} - {self.gdd.title}"
    
    class Meta:
        ordering = ['order']

class GDDComment(TimeStampedModel):
    """
    Comments on specific sections of the GDD
    """
    section = models.ForeignKey(GDDSection, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    text = models.TextField()
    resolved = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Comment on {self.section.title} by {self.author.username}"
    
    class Meta:
        ordering = ['created']
