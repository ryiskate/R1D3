from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse


class KnowledgeCategory(models.Model):
    """Category for organizing knowledge articles"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default="fa-book", help_text="FontAwesome icon class")
    color = models.CharField(max_length=20, default="#4e73df", help_text="Hex color code")
    order = models.PositiveIntegerField(default=0, help_text="Display order")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Knowledge Category"
        verbose_name_plural = "Knowledge Categories"
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('education:knowledge_category', kwargs={'slug': self.slug})
    
    def article_count(self):
        return self.articles.count()


class KnowledgeTag(models.Model):
    """Tags for knowledge articles"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    
    class Meta:
        verbose_name = "Knowledge Tag"
        verbose_name_plural = "Knowledge Tags"
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('education:knowledge_tag', kwargs={'slug': self.slug})
    
    def article_count(self):
        return self.articles.count()


class KnowledgeArticle(models.Model):
    """Main model for knowledge articles"""
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    summary = models.TextField(help_text="Brief summary of the article")
    content = models.TextField(help_text="Main content in HTML format")
    category = models.ForeignKey(
        KnowledgeCategory, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='articles'
    )
    tags = models.ManyToManyField(KnowledgeTag, blank=True, related_name='articles')
    featured_image = models.ImageField(
        upload_to='knowledge/images/', 
        blank=True, 
        null=True,
        help_text="Featured image for the article"
    )
    is_published = models.BooleanField(default=True)
    view_count = models.PositiveIntegerField(default=0)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Knowledge Article"
        verbose_name_plural = "Knowledge Articles"
        ordering = ['-updated_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('education:knowledge_article', kwargs={'slug': self.slug})
    
    def increment_view_count(self):
        self.view_count += 1
        self.save(update_fields=['view_count'])
    
    def get_related_articles(self, limit=3):
        """Get related articles based on tags"""
        if not self.tags.exists():
            return KnowledgeArticle.objects.filter(
                is_published=True
            ).exclude(id=self.id).order_by('-updated_at')[:limit]
        
        return KnowledgeArticle.objects.filter(
            tags__in=self.tags.all(),
            is_published=True
        ).exclude(id=self.id).distinct().order_by('-updated_at')[:limit]


class MediaAttachment(models.Model):
    """Media attachments for knowledge articles"""
    article = models.ForeignKey(
        KnowledgeArticle, 
        on_delete=models.CASCADE, 
        related_name='attachments'
    )
    file = models.FileField(upload_to='knowledge/attachments/')
    file_type = models.CharField(
        max_length=50,
        choices=[
            ('image', 'Image'),
            ('video', 'Video'),
            ('document', 'Document'),
            ('audio', 'Audio'),
            ('other', 'Other')
        ],
        default='image'
    )
    title = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Media Attachment"
        verbose_name_plural = "Media Attachments"
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.get_file_type_display()} - {self.title or self.file.name}"
    
    @property
    def filename(self):
        return self.file.name.split('/')[-1]
