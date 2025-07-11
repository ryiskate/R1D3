from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.db import transaction
from django.contrib import messages
from django.template.loader import render_to_string

# Import WeasyPrint only when needed to avoid issues during migrations
weasyprint_imported = False
try:
    from weasyprint import HTML
    from weasyprint.text.fonts import FontConfiguration
    weasyprint_imported = True
except ImportError:
    pass

from core.mixins import BreadcrumbMixin
from .models import Course, ConceptSection, AdvancedTopicSection, PracticalExample, GlossaryTerm
from .forms import (
    CourseForm, 
    ConceptSectionFormSet, 
    AdvancedTopicSectionFormSet, 
    PracticalExampleFormSet, 
    GlossaryTermFormSet
)


class CourseListView(BreadcrumbMixin, LoginRequiredMixin, ListView):
    """View for listing all courses"""
    model = Course
    template_name = 'education/course/list.html'
    context_object_name = 'courses'
    
    def get_breadcrumbs(self):
        return [
            {'title': 'Education', 'url': reverse('education:dashboard')},
            {'title': 'Courses', 'url': None}
        ]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_department'] = 'education'
        return context


class CourseDetailView(BreadcrumbMixin, LoginRequiredMixin, DetailView):
    """View for displaying a single course"""
    model = Course
    template_name = 'education/course/detail.html'
    context_object_name = 'course'
    
    def get_breadcrumbs(self):
        doc = self.get_object()
        return [
            {'title': 'Education', 'url': reverse('education:dashboard')},
            {'title': 'Courses', 'url': reverse('education:course_list')},
            {'title': doc.title, 'url': None}
        ]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_department'] = 'education'
        
        # Get related objects
        context['concepts'] = self.object.concepts.all().order_by('order')
        context['advanced_topics'] = self.object.advanced_topics.all().order_by('order')
        context['practical_examples'] = self.object.practical_examples.all().order_by('order')
        context['glossary_terms'] = self.object.glossary_terms.all().order_by('term')
        
        return context


class CourseCreateView(BreadcrumbMixin, LoginRequiredMixin, TemplateView):
    """View for creating a new course"""
    template_name = 'education/course/form.html'
    
    def get_breadcrumbs(self):
        return [
            {'title': 'Education', 'url': reverse('education:dashboard')},
            {'title': 'Courses', 'url': reverse('education:course_list')},
            {'title': 'Create New', 'url': None}
        ]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_department'] = 'education'
        context['form'] = CourseForm()
        
        if self.request.POST:
            context['concept_formset'] = ConceptSectionFormSet(self.request.POST)
            context['advanced_topic_formset'] = AdvancedTopicSectionFormSet(self.request.POST)
            context['practical_example_formset'] = PracticalExampleFormSet(self.request.POST)
            context['glossary_formset'] = GlossaryTermFormSet(self.request.POST)
        else:
            context['concept_formset'] = ConceptSectionFormSet()
            context['advanced_topic_formset'] = AdvancedTopicSectionFormSet()
            context['practical_example_formset'] = PracticalExampleFormSet()
            context['glossary_formset'] = GlossaryTermFormSet()
        
        return context
    
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        form = CourseForm(request.POST)
        
        if form.is_valid():
            # Save the main form first to get a course instance
            course = form.save(commit=False)
            course.author = request.user
            course.save()
            
            # Now create formsets with the course instance
            concept_formset = ConceptSectionFormSet(request.POST, instance=course)
            advanced_topic_formset = AdvancedTopicSectionFormSet(request.POST, instance=course)
            practical_example_formset = PracticalExampleFormSet(request.POST, instance=course)
            glossary_formset = GlossaryTermFormSet(request.POST, instance=course)
            
            # Validate formsets
            formsets_valid = (
                concept_formset.is_valid() and 
                advanced_topic_formset.is_valid() and 
                practical_example_formset.is_valid() and 
                glossary_formset.is_valid()
            )
            
            if formsets_valid:
                # Save all formsets
                concept_formset.save()
                advanced_topic_formset.save()
                practical_example_formset.save()
                glossary_formset.save()
                
                messages.success(request, f"Course '{course.title}' created successfully.")
                return redirect('education:course_detail', pk=course.pk)
            else:
                # If formsets are not valid, we need to delete the course we just created
                course.delete()
        
        # If form is not valid or formsets are not valid, re-render with errors
        context = self.get_context_data()
        context['form'] = form
        
        # Re-initialize formsets with POST data
        context['concept_formset'] = ConceptSectionFormSet(request.POST)
        context['advanced_topic_formset'] = AdvancedTopicSectionFormSet(request.POST)
        context['practical_example_formset'] = PracticalExampleFormSet(request.POST)
        context['glossary_formset'] = GlossaryTermFormSet(request.POST)
        
        return self.render_to_response(context)


class CourseUpdateView(BreadcrumbMixin, LoginRequiredMixin, TemplateView):
    """View for updating an existing course"""
    template_name = 'education/course/form.html'
    
    def get_breadcrumbs(self):
        doc = get_object_or_404(Course, pk=self.kwargs['pk'])
        return [
            {'title': 'Education', 'url': reverse('education:dashboard')},
            {'title': 'Courses', 'url': reverse('education:course_list')},
            {'title': doc.title, 'url': reverse('education:course_detail', kwargs={'pk': doc.pk})},
            {'title': 'Edit', 'url': None}
        ]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_department'] = 'education'
        course = get_object_or_404(Course, pk=self.kwargs['pk'])
        
        if self.request.POST:
            context['form'] = CourseForm(self.request.POST, instance=course)
            context['concept_formset'] = ConceptSectionFormSet(self.request.POST, instance=course)
            context['advanced_topic_formset'] = AdvancedTopicSectionFormSet(self.request.POST, instance=course)
            context['practical_example_formset'] = PracticalExampleFormSet(self.request.POST, instance=course)
            context['glossary_formset'] = GlossaryTermFormSet(self.request.POST, instance=course)
        else:
            context['form'] = CourseForm(instance=course)
            context['concept_formset'] = ConceptSectionFormSet(instance=course)
            context['advanced_topic_formset'] = AdvancedTopicSectionFormSet(instance=course)
            context['practical_example_formset'] = PracticalExampleFormSet(instance=course)
            context['glossary_formset'] = GlossaryTermFormSet(instance=course)
        
        context['is_update'] = True
        context['course'] = course
        return context
    
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        course = get_object_or_404(Course, pk=self.kwargs['pk'])
        form = CourseForm(request.POST, instance=course)
        concept_formset = ConceptSectionFormSet(request.POST, instance=course)
        advanced_topic_formset = AdvancedTopicSectionFormSet(request.POST, instance=course)
        practical_example_formset = PracticalExampleFormSet(request.POST, instance=course)
        glossary_formset = GlossaryTermFormSet(request.POST, instance=course)
        
        if (form.is_valid() and concept_formset.is_valid() and 
            advanced_topic_formset.is_valid() and practical_example_formset.is_valid() and 
            glossary_formset.is_valid()):
            
            # Save the main form
            course = form.save()
            
            # Save formsets
            concept_formset.save()
            advanced_topic_formset.save()
            practical_example_formset.save()
            glossary_formset.save()
            
            messages.success(request, f"Course '{course.title}' updated successfully.")
            return redirect('education:course_detail', pk=course.pk)
        
        # If form is not valid, re-render with errors
        context = self.get_context_data()
        context['form'] = form
        context['concept_formset'] = concept_formset
        context['advanced_topic_formset'] = advanced_topic_formset
        context['practical_example_formset'] = practical_example_formset
        context['glossary_formset'] = glossary_formset
        return self.render_to_response(context)


class CourseDeleteView(BreadcrumbMixin, LoginRequiredMixin, DeleteView):
    """View for deleting a course"""
    model = Course
    template_name = 'education/course/confirm_delete.html'
    success_url = reverse_lazy('education:course_list')
    
    def get_breadcrumbs(self):
        doc = self.get_object()
        return [
            {'title': 'Education', 'url': reverse('education:dashboard')},
            {'title': 'Courses', 'url': reverse('education:course_list')},
            {'title': doc.title, 'url': reverse('education:course_detail', kwargs={'pk': doc.pk})},
            {'title': 'Delete', 'url': None}
        ]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_department'] = 'education'
        return context


class CoursePDFView(LoginRequiredMixin, View):
    """View for exporting a course as PDF"""
    
    def get(self, request, *args, **kwargs):
        # Check if WeasyPrint is available
        if not weasyprint_imported:
            messages.error(request, "PDF export is not available. WeasyPrint library is not installed.")
            return redirect('education:course_detail', pk=self.kwargs['pk'])
            
        # Get the course object
        course = get_object_or_404(Course, pk=self.kwargs['pk'])
        
        # Get related objects
        concepts = course.concepts.all().order_by('order')
        advanced_topics = course.advanced_topics.all().order_by('order')
        practical_examples = course.practical_examples.all().order_by('order')
        glossary_terms = course.glossary_terms.all().order_by('term')
        
        # Prepare context for the template
        context = {
            'course': course,
            'concepts': concepts,
            'advanced_topics': advanced_topics,
            'practical_examples': practical_examples,
            'glossary_terms': glossary_terms,
        }
        
        # Render the template to a string
        html_string = render_to_string('education/course/pdf_template.html', context)
        
        try:
            # Generate PDF
            font_config = FontConfiguration()
            html = HTML(string=html_string, base_url=request.build_absolute_uri('/'))
            pdf = html.write_pdf(font_config=font_config)
            
            # Create HTTP response with PDF
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{course.title}.pdf"'
            
            return response
        except Exception as e:
            messages.error(request, f"Error generating PDF: {str(e)}")
            return redirect('education:course_detail', pk=course.pk)
