from django.db import models
from django.contrib.auth.models import User
from django.core.validators import URLValidator


class TimeStampedModel(models.Model):
    """
    An abstract base class model that provides self-updating
    created and modified fields.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class QuickLink(TimeStampedModel):
    """
    Custom quick links for the side menu
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quick_links')
    name = models.CharField(max_length=50)
    url = models.CharField(max_length=255, validators=[URLValidator(schemes=['http', 'https', '/'])])
    icon = models.CharField(max_length=50, default='fas fa-link')
    position = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['position']
        
    def __str__(self):
        return f"{self.name} ({self.user.username})"


class Profile(TimeStampedModel):
    """
    Extended user profile with additional information
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    job_title = models.CharField(max_length=100, blank=True)
    department = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
