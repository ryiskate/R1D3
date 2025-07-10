from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseRedirect
from django.db import transaction
from django.contrib import messages

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
        concept_formset = ConceptSectionFormSet(request.POST)
        advanced_topic_formset = AdvancedTopicSectionFormSet(request.POST)
        practical_example_formset = PracticalExampleFormSet(request.POST)
        glossary_formset = GlossaryTermFormSet(request.POST)
        
        if (form.is_valid() and concept_formset.is_valid() and 
            advanced_topic_formset.is_valid() and practical_example_formset.is_valid() and 
            glossary_formset.is_valid()):
            
            # Save the main form
            course = form.save(commit=False)
            course.author = request.user
            course.save()
            
            # Save formsets
            concept_formset.instance = course
            concept_formset.save()
            
            advanced_topic_formset.instance = course
            advanced_topic_formset.save()
            
            practical_example_formset.instance = course
            practical_example_formset.save()
            
            glossary_formset.instance = course
            glossary_formset.save()
            
            messages.success(request, f"Course '{course.title}' created successfully.")
            return redirect('education:course_detail', pk=course.pk)
        
        # If form is not valid, re-render with errors
        context = self.get_context_data()
        context['form'] = form
        context['concept_formset'] = concept_formset
        context['advanced_topic_formset'] = advanced_topic_formset
        context['practical_example_formset'] = practical_example_formset
        context['glossary_formset'] = glossary_formset
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
