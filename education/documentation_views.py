from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseRedirect
from django.db import transaction
from django.contrib import messages

from core.mixins import BreadcrumbMixin
from .models import CourseDocumentation, ConceptSection, AdvancedTopicSection, PracticalExample, GlossaryTerm
from .forms import (
    CourseDocumentationForm, 
    ConceptSectionFormSet, 
    AdvancedTopicSectionFormSet, 
    PracticalExampleFormSet, 
    GlossaryTermFormSet
)


class DocumentationListView(BreadcrumbMixin, LoginRequiredMixin, ListView):
    """View for listing all course documentations"""
    model = CourseDocumentation
    template_name = 'education/documentation/list.html'
    context_object_name = 'documentations'
    
    def get_breadcrumbs(self):
        return [
            {'title': 'Education', 'url': reverse('education:dashboard')},
            {'title': 'Documentation', 'url': None}
        ]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_department'] = 'education'
        return context


class DocumentationDetailView(BreadcrumbMixin, LoginRequiredMixin, DetailView):
    """View for displaying a single course documentation"""
    model = CourseDocumentation
    template_name = 'education/documentation/detail.html'
    context_object_name = 'documentation'
    
    def get_breadcrumbs(self):
        doc = self.get_object()
        return [
            {'title': 'Education', 'url': reverse('education:dashboard')},
            {'title': 'Documentation', 'url': reverse('education:documentation_list')},
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


class DocumentationCreateView(BreadcrumbMixin, LoginRequiredMixin, TemplateView):
    """View for creating a new course documentation"""
    template_name = 'education/documentation/form.html'
    
    def get_breadcrumbs(self):
        return [
            {'title': 'Education', 'url': reverse('education:dashboard')},
            {'title': 'Documentation', 'url': reverse('education:documentation_list')},
            {'title': 'Create New', 'url': None}
        ]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_department'] = 'education'
        context['form'] = CourseDocumentationForm()
        
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
        form = CourseDocumentationForm(request.POST)
        concept_formset = ConceptSectionFormSet(request.POST)
        advanced_topic_formset = AdvancedTopicSectionFormSet(request.POST)
        practical_example_formset = PracticalExampleFormSet(request.POST)
        glossary_formset = GlossaryTermFormSet(request.POST)
        
        if (form.is_valid() and concept_formset.is_valid() and 
            advanced_topic_formset.is_valid() and practical_example_formset.is_valid() and 
            glossary_formset.is_valid()):
            
            # Save the main form
            documentation = form.save(commit=False)
            documentation.author = request.user
            documentation.save()
            
            # Save formsets
            concept_formset.instance = documentation
            concept_formset.save()
            
            advanced_topic_formset.instance = documentation
            advanced_topic_formset.save()
            
            practical_example_formset.instance = documentation
            practical_example_formset.save()
            
            glossary_formset.instance = documentation
            glossary_formset.save()
            
            messages.success(request, f"Documentation '{documentation.title}' created successfully.")
            return redirect('education:documentation_detail', pk=documentation.pk)
        
        # If form is not valid, re-render with errors
        context = self.get_context_data()
        context['form'] = form
        context['concept_formset'] = concept_formset
        context['advanced_topic_formset'] = advanced_topic_formset
        context['practical_example_formset'] = practical_example_formset
        context['glossary_formset'] = glossary_formset
        return self.render_to_response(context)


class DocumentationUpdateView(BreadcrumbMixin, LoginRequiredMixin, TemplateView):
    """View for updating an existing course documentation"""
    template_name = 'education/documentation/form.html'
    
    def get_breadcrumbs(self):
        doc = get_object_or_404(CourseDocumentation, pk=self.kwargs['pk'])
        return [
            {'title': 'Education', 'url': reverse('education:dashboard')},
            {'title': 'Documentation', 'url': reverse('education:documentation_list')},
            {'title': doc.title, 'url': reverse('education:documentation_detail', kwargs={'pk': doc.pk})},
            {'title': 'Edit', 'url': None}
        ]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_department'] = 'education'
        documentation = get_object_or_404(CourseDocumentation, pk=self.kwargs['pk'])
        
        if self.request.POST:
            context['form'] = CourseDocumentationForm(self.request.POST, instance=documentation)
            context['concept_formset'] = ConceptSectionFormSet(self.request.POST, instance=documentation)
            context['advanced_topic_formset'] = AdvancedTopicSectionFormSet(self.request.POST, instance=documentation)
            context['practical_example_formset'] = PracticalExampleFormSet(self.request.POST, instance=documentation)
            context['glossary_formset'] = GlossaryTermFormSet(self.request.POST, instance=documentation)
        else:
            context['form'] = CourseDocumentationForm(instance=documentation)
            context['concept_formset'] = ConceptSectionFormSet(instance=documentation)
            context['advanced_topic_formset'] = AdvancedTopicSectionFormSet(instance=documentation)
            context['practical_example_formset'] = PracticalExampleFormSet(instance=documentation)
            context['glossary_formset'] = GlossaryTermFormSet(instance=documentation)
        
        context['is_update'] = True
        context['documentation'] = documentation
        return context
    
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        documentation = get_object_or_404(CourseDocumentation, pk=self.kwargs['pk'])
        form = CourseDocumentationForm(request.POST, instance=documentation)
        concept_formset = ConceptSectionFormSet(request.POST, instance=documentation)
        advanced_topic_formset = AdvancedTopicSectionFormSet(request.POST, instance=documentation)
        practical_example_formset = PracticalExampleFormSet(request.POST, instance=documentation)
        glossary_formset = GlossaryTermFormSet(request.POST, instance=documentation)
        
        if (form.is_valid() and concept_formset.is_valid() and 
            advanced_topic_formset.is_valid() and practical_example_formset.is_valid() and 
            glossary_formset.is_valid()):
            
            # Save the main form
            documentation = form.save()
            
            # Save formsets
            concept_formset.save()
            advanced_topic_formset.save()
            practical_example_formset.save()
            glossary_formset.save()
            
            messages.success(request, f"Documentation '{documentation.title}' updated successfully.")
            return redirect('education:documentation_detail', pk=documentation.pk)
        
        # If form is not valid, re-render with errors
        context = self.get_context_data()
        context['form'] = form
        context['concept_formset'] = concept_formset
        context['advanced_topic_formset'] = advanced_topic_formset
        context['practical_example_formset'] = practical_example_formset
        context['glossary_formset'] = glossary_formset
        return self.render_to_response(context)


class DocumentationDeleteView(BreadcrumbMixin, LoginRequiredMixin, DeleteView):
    """View for deleting a course documentation"""
    model = CourseDocumentation
    template_name = 'education/documentation/confirm_delete.html'
    success_url = reverse_lazy('education:documentation_list')
    
    def get_breadcrumbs(self):
        doc = self.get_object()
        return [
            {'title': 'Education', 'url': reverse('education:dashboard')},
            {'title': 'Documentation', 'url': reverse('education:documentation_list')},
            {'title': doc.title, 'url': reverse('education:documentation_detail', kwargs={'pk': doc.pk})},
            {'title': 'Delete', 'url': None}
        ]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_department'] = 'education'
        return context
