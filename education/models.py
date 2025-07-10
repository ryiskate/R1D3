from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.urls import reverse

User = get_user_model()


class Course(models.Model):
    """
    Model for comprehensive course content based on a structured template
    """
    # 1. Initial Information
    title = models.CharField(max_length=255, verbose_name="Document Title")
    central_theme = models.CharField(max_length=255, verbose_name="Central Theme")
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='course_documents')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objective = models.TextField(verbose_name="Document Objective")
    
    # 2. Summary
    summary = models.TextField(verbose_name="Theme Summary")
    
    # 3. Introduction
    introduction = models.TextField(verbose_name="Introduction to Theme")
    practical_applications = models.TextField(verbose_name="Practical Applications")
    
    # 4. Fundamental Concepts
    # These will be handled by the ConceptSection model
    
    # 5. Advanced Topics
    # These will be handled by the AdvancedTopicSection model
    
    # 6. Practical Examples
    # These will be handled by the PracticalExample model
    
    # 7. Resources
    recommended_resources = models.TextField(verbose_name="Recommended Resources", blank=True)
    
    # 8. Glossary
    # This will be handled by the GlossaryTerm model
    
    # 9. Attachments
    attachments = models.TextField(verbose_name="Attachments", blank=True, help_text="Links to exercises, important resources, etc.")
    
    # Status field for workflow
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('review', 'In Review'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    class Meta:
        verbose_name = "Course"
        verbose_name_plural = "Courses"
        ordering = ['-updated_at']
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('education:course_detail', kwargs={'pk': self.pk})


class ConceptSection(models.Model):
    """
    Model for fundamental concepts within a course
    """
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='concepts')
    name = models.CharField(max_length=255, verbose_name="Concept Name")
    definition = models.TextField(verbose_name="Definition")
    detailed_explanation = models.TextField(verbose_name="Detailed Explanation")
    illustrative_example = models.TextField(verbose_name="Illustrative Example")
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order']
        verbose_name = "Concept Section"
        verbose_name_plural = "Concept Sections"
    
    def __str__(self):
        return f"{self.name} - {self.course.title}"


class AdvancedTopicSection(models.Model):
    """
    Model for advanced topics within a course
    """
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='advanced_topics')
    name = models.CharField(max_length=255, verbose_name="Topic Name")
    applications = models.TextField(verbose_name="Applications")
    challenges = models.TextField(verbose_name="Risks/Challenges")
    real_example = models.TextField(verbose_name="Real-world Example")
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order']
        verbose_name = "Advanced Topic"
        verbose_name_plural = "Advanced Topics"
    
    def __str__(self):
        return f"{self.name} - {self.course.title}"


class PracticalExample(models.Model):
    """
    Model for practical examples within a course
    """
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='practical_examples')
    title = models.CharField(max_length=255, verbose_name="Example Title")
    code = models.TextField(verbose_name="Code", blank=True)
    image = models.URLField(verbose_name="Image URL", blank=True)
    step_by_step = models.TextField(verbose_name="Step-by-step Explanation")
    real_application = models.TextField(verbose_name="Application in Real Project", blank=True)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order']
        verbose_name = "Practical Example"
        verbose_name_plural = "Practical Examples"
    
    def __str__(self):
        return f"{self.title} - {self.course.title}"


class GlossaryTerm(models.Model):
    """
    Model for glossary terms within a course
    """
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='glossary_terms')
    term = models.CharField(max_length=255, verbose_name="Term")
    definition = models.TextField(verbose_name="Definition")
    
    class Meta:
        ordering = ['term']
        verbose_name = "Glossary Term"
        verbose_name_plural = "Glossary Terms"
    
    def __str__(self):
        return f"{self.term} - {self.course.title}"
