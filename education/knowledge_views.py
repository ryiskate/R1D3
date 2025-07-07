from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse
from django.db.models import Q
from django.contrib import messages
from django.utils.text import slugify

from core.mixins import BreadcrumbMixin
from .knowledge_models import KnowledgeArticle, KnowledgeCategory, KnowledgeTag, MediaAttachment
from .knowledge_forms import KnowledgeArticleForm, MediaAttachmentForm


class KnowledgeBaseView(LoginRequiredMixin, BreadcrumbMixin, ListView):
    """Main view for the Knowledge Base dashboard"""
    model = KnowledgeArticle
    template_name = 'education/knowledge/dashboard.html'
    context_object_name = 'articles'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = KnowledgeArticle.objects.filter(is_published=True)
        
        # Filter by category if provided
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        # Filter by tag if provided
        tag_slug = self.request.GET.get('tag')
        if tag_slug:
            queryset = queryset.filter(tags__slug=tag_slug)
        
        # Search if provided
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) | 
                Q(summary__icontains=search_query) |
                Q(content__icontains=search_query)
            )
        
        return queryset.order_by('-updated_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_department'] = 'education'
        context['categories'] = KnowledgeCategory.objects.all()
        context['popular_tags'] = KnowledgeTag.objects.all()[:10]
        context['recent_articles'] = KnowledgeArticle.objects.filter(
            is_published=True
        ).order_by('-created_at')[:5]
        
        # Get active filters
        context['active_category'] = self.request.GET.get('category', '')
        context['active_tag'] = self.request.GET.get('tag', '')
        context['search_query'] = self.request.GET.get('q', '')
        
        return context
    
    def get_breadcrumbs(self):
        breadcrumbs = [
            {'title': 'Education', 'url': reverse('education:dashboard')},
            {'title': 'Knowledge Base', 'url': reverse('education:knowledge_base')},
        ]
        return breadcrumbs


class KnowledgeArticleDetailView(LoginRequiredMixin, BreadcrumbMixin, DetailView):
    """View for displaying a knowledge article"""
    model = KnowledgeArticle
    template_name = 'education/knowledge/article_detail.html'
    context_object_name = 'article'
    slug_url_kwarg = 'slug'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_department'] = 'education'
        context['related_articles'] = self.object.get_related_articles()
        return context
    
    def get_breadcrumbs(self):
        article = self.get_object()
        breadcrumbs = [
            {'title': 'Education', 'url': reverse('education:dashboard')},
            {'title': 'Knowledge Base', 'url': reverse('education:knowledge_base')},
        ]
        
        if article.category:
            breadcrumbs.append({
                'title': article.category.name,
                'url': reverse('education:knowledge_category', kwargs={'slug': article.category.slug})
            })
        
        breadcrumbs.append({'title': article.title, 'url': '#'})
        return breadcrumbs
    
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        # Increment view count
        self.object.increment_view_count()
        return response


class KnowledgeArticleCreateView(LoginRequiredMixin, BreadcrumbMixin, CreateView):
    """View for creating a new knowledge article"""
    model = KnowledgeArticle
    form_class = KnowledgeArticleForm
    template_name = 'education/knowledge/article_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_department'] = 'education'
        context['is_create'] = True
        return context
    
    def get_breadcrumbs(self):
        breadcrumbs = [
            {'title': 'Education', 'url': reverse('education:dashboard')},
            {'title': 'Knowledge Base', 'url': reverse('education:knowledge_base')},
            {'title': 'Create Article', 'url': '#'},
        ]
        return breadcrumbs
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, f"Article '{self.object.title}' created successfully.")
        return response


class KnowledgeArticleUpdateView(LoginRequiredMixin, BreadcrumbMixin, UpdateView):
    """View for updating a knowledge article"""
    model = KnowledgeArticle
    form_class = KnowledgeArticleForm
    template_name = 'education/knowledge/article_form.html'
    slug_url_kwarg = 'slug'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_department'] = 'education'
        context['is_create'] = False
        context['media_form'] = MediaAttachmentForm()
        context['media_attachments'] = self.object.attachments.all()
        return context
    
    def get_breadcrumbs(self):
        article = self.get_object()
        breadcrumbs = [
            {'title': 'Education', 'url': reverse('education:dashboard')},
            {'title': 'Knowledge Base', 'url': reverse('education:knowledge_base')},
            {'title': article.title, 'url': article.get_absolute_url()},
            {'title': 'Edit', 'url': '#'},
        ]
        return breadcrumbs
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Article '{self.object.title}' updated successfully.")
        return response


class KnowledgeArticleDeleteView(LoginRequiredMixin, BreadcrumbMixin, DeleteView):
    """View for deleting a knowledge article"""
    model = KnowledgeArticle
    template_name = 'education/knowledge/article_confirm_delete.html'
    success_url = reverse_lazy('education:knowledge_base')
    slug_url_kwarg = 'slug'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_department'] = 'education'
        return context
    
    def get_breadcrumbs(self):
        article = self.get_object()
        breadcrumbs = [
            {'title': 'Education', 'url': reverse('education:dashboard')},
            {'title': 'Knowledge Base', 'url': reverse('education:knowledge_base')},
            {'title': article.title, 'url': article.get_absolute_url()},
            {'title': 'Delete', 'url': '#'},
        ]
        return breadcrumbs
    
    def delete(self, request, *args, **kwargs):
        article = self.get_object()
        title = article.title
        response = super().delete(request, *args, **kwargs)
        messages.success(request, f"Article '{title}' deleted successfully.")
        return response


class KnowledgeCategoryView(LoginRequiredMixin, BreadcrumbMixin, ListView):
    """View for displaying articles in a specific category"""
    model = KnowledgeArticle
    template_name = 'education/knowledge/category.html'
    context_object_name = 'articles'
    paginate_by = 12
    
    def get_queryset(self):
        self.category = get_object_or_404(KnowledgeCategory, slug=self.kwargs['slug'])
        return KnowledgeArticle.objects.filter(
            category=self.category,
            is_published=True
        ).order_by('-updated_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_department'] = 'education'
        context['category'] = self.category
        context['categories'] = KnowledgeCategory.objects.all()
        context['popular_tags'] = KnowledgeTag.objects.all()[:10]
        return context
    
    def get_breadcrumbs(self):
        category = get_object_or_404(KnowledgeCategory, slug=self.kwargs['slug'])
        breadcrumbs = [
            {'title': 'Education', 'url': reverse('education:dashboard')},
            {'title': 'Knowledge Base', 'url': reverse('education:knowledge_base')},
            {'title': category.name, 'url': '#'},
        ]
        return breadcrumbs


class KnowledgeTagView(LoginRequiredMixin, BreadcrumbMixin, ListView):
    """View for displaying articles with a specific tag"""
    model = KnowledgeArticle
    template_name = 'education/knowledge/tag.html'
    context_object_name = 'articles'
    paginate_by = 12
    
    def get_queryset(self):
        self.tag = get_object_or_404(KnowledgeTag, slug=self.kwargs['slug'])
        return KnowledgeArticle.objects.filter(
            tags=self.tag,
            is_published=True
        ).order_by('-updated_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_department'] = 'education'
        context['tag'] = self.tag
        context['categories'] = KnowledgeCategory.objects.all()
        context['popular_tags'] = KnowledgeTag.objects.all()[:10]
        return context
    
    def get_breadcrumbs(self):
        tag = get_object_or_404(KnowledgeTag, slug=self.kwargs['slug'])
        breadcrumbs = [
            {'title': 'Education', 'url': reverse('education:dashboard')},
            {'title': 'Knowledge Base', 'url': reverse('education:knowledge_base')},
            {'title': f'Tag: {tag.name}', 'url': '#'},
        ]
        return breadcrumbs


class MediaAttachmentUploadView(LoginRequiredMixin, View):
    """View for uploading media attachments to an article"""
    
    def post(self, request, slug):
        article = get_object_or_404(KnowledgeArticle, slug=slug)
        form = MediaAttachmentForm(request.POST, request.FILES)
        
        if form.is_valid():
            attachment = form.save(commit=False)
            attachment.article = article
            attachment.save()
            
            return JsonResponse({
                'success': True,
                'id': attachment.id,
                'url': attachment.file.url,
                'title': attachment.title,
                'file_type': attachment.get_file_type_display(),
                'filename': attachment.filename
            })
        
        return JsonResponse({'success': False, 'errors': form.errors}, status=400)


class MediaAttachmentDeleteView(LoginRequiredMixin, View):
    """View for deleting media attachments"""
    
    def post(self, request, pk):
        attachment = get_object_or_404(MediaAttachment, pk=pk)
        article_slug = attachment.article.slug
        attachment.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Attachment deleted successfully.'
        })
