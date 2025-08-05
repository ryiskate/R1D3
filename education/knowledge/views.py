from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView, View, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.http import JsonResponse, HttpResponseRedirect
from django.db.models import Q

from core.mixins import BreadcrumbMixin
from .models import KnowledgeArticle, KnowledgeCategory, KnowledgeTag, MediaAttachment
from .forms import KnowledgeArticleForm, MediaAttachmentForm

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
        import logging
        import json
        logger = logging.getLogger(__name__)
        
        context = super().get_context_data(**kwargs)
        context['active_department'] = 'education'
        context['related_articles'] = self.object.get_related_articles()
        
        # Process content blocks if they exist
        article = self.object
        if article.content and article.content.startswith('Content blocks:'):
            # Content blocks should be stored directly in the database model
            if article.content_blocks:
                # Content blocks are already in the model, no need to parse JSON
                logger.info(f"Using content blocks from database for article {article.id}: {len(article.content_blocks)} blocks")
                # The template already has access to article.content_blocks
                
                # Log the content blocks for debugging
                try:
                    logger.info(f"Content blocks data: {json.dumps(article.content_blocks)[:200]}...")
                except Exception as e:
                    logger.error(f"Error serializing content blocks for logging: {str(e)}")
            else:
                # No content blocks found in the database
                logger.warning(f"No content blocks found in database for article {article.id}")
                context['content_blocks_missing'] = True
        
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
    
    def get_success_url(self):
        """Return the URL to redirect to after processing a valid form."""
        return self.object.get_absolute_url()
    
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
        import logging
        import json
        logger = logging.getLogger(__name__)
        
        # Set the author to the current user
        form.instance.author = self.request.user
        
        # Process content blocks data if provided
        content_blocks = self.request.POST.get('content_blocks')
        logger.info(f"Content blocks data received: {content_blocks[:100] if content_blocks else 'None'}...")
        
        # Store content blocks directly in the database model
        if content_blocks:
            try:
                # Parse the JSON content blocks
                content_blocks_json = json.loads(content_blocks)
                # Store the parsed JSON in the content_blocks field
                form.instance.content_blocks = content_blocks_json
                # Store a marker in the content field that this article uses content blocks
                form.instance.content = f"Content blocks: {len(content_blocks_json)} blocks"
                logger.info(f"Parsed content blocks: {len(content_blocks_json)} blocks")
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing content blocks JSON: {str(e)}")
                # If JSON parsing fails, store the content as is
                form.instance.content = content_blocks if content_blocks else ""
                form.instance.content_blocks = None
        
        # Ensure the slug is set if not provided
        from django.utils.text import slugify
        if not form.instance.slug:
            form.instance.slug = slugify(form.instance.title)
        logger.info(f"Using slug: {form.instance.slug}")
        
        # Save the form
        try:
            self.object = form.save()
            logger.info(f"Article saved with ID: {self.object.id}, slug: {self.object.slug}")
            logger.info(f"Content blocks saved to database: {bool(form.instance.content_blocks)}")
            
            # Add success message
            messages.success(self.request, f"Article '{self.object.title}' created successfully.")
            
            # Get the absolute URL for the article
            redirect_url = self.object.get_absolute_url()
            logger.info(f"Redirecting to: {redirect_url}")
            
            # Check if this is an AJAX request
            is_ajax = self.request.headers.get('X-Requested-With') == 'XMLHttpRequest'
            logger.info(f"Is AJAX request: {is_ajax}")
            
            if is_ajax:
                # Return JSON response for AJAX requests with full URL
                # Include the full URL to avoid any client-side URL construction issues
                full_redirect_url = self.request.build_absolute_uri(redirect_url)
                logger.info(f"Full redirect URL for AJAX: {full_redirect_url}")
                
                return JsonResponse({
                    'success': True,
                    'redirect_url': full_redirect_url,
                    'slug': self.object.slug,
                    'article_id': self.object.id,
                    'message': f"Article '{self.object.title}' created successfully."
                })
            else:
                # Use HttpResponseRedirect for standard form submissions
                from django.http import HttpResponseRedirect
                response = HttpResponseRedirect(redirect_url)
                response['X-Article-Created'] = 'True'
                response['X-Article-Slug'] = self.object.slug
                logger.info(f"Returning HttpResponseRedirect to {redirect_url}")
                return response
        except Exception as e:
            logger.error(f"Error saving article: {str(e)}")
            # Re-raise the exception to let Django handle it
            raise


class KnowledgeArticleUpdateView(LoginRequiredMixin, BreadcrumbMixin, UpdateView):
    """View for updating a knowledge article"""
    model = KnowledgeArticle
    form_class = KnowledgeArticleForm
    template_name = 'education/knowledge/article_form.html'
    
    def get_success_url(self):
        """Return the URL to redirect to after processing a valid form."""
        return self.object.get_absolute_url()
    slug_url_kwarg = 'slug'
    
    def get_form(self, form_class=None):
        """Return an instance of the form to be used in this view."""
        import logging
        logger = logging.getLogger(__name__)
        
        form = super().get_form(form_class)
        logger.info(f"Form instance data: {form.instance.id}, {form.instance.title if form.instance else 'None'}")
        return form
    
    # Note: The form_valid method is defined below to avoid duplication
    
    def get_context_data(self, **kwargs):
        import json
        import logging
        logger = logging.getLogger(__name__)
        
        context = super().get_context_data(**kwargs)
        context['active_department'] = 'education'
        context['is_create'] = False
        context['article'] = self.object  # Ensure article is explicitly set in context
        logger.info(f"Update view context: is_create={context['is_create']}, article.slug={self.object.slug if self.object else 'None'}")
        
        context['media_form'] = MediaAttachmentForm()
        context['media_attachments'] = self.object.attachments.all()
        
        # Process content blocks if they exist
        article = self.object
        if article.content and article.content.startswith('Content blocks:'):
            try:
                # Get content blocks from the database JSONField
                if article.content_blocks:
                    # Convert content blocks from database to JSON string for the template
                    content_blocks_json = json.dumps(article.content_blocks)
                    context['content_blocks_json'] = content_blocks_json
                    logger.info(f"Loaded content blocks from database for article {article.id}: {len(article.content_blocks)} blocks")
                else:
                    # No content blocks found in database
                    logger.warning(f"No content blocks found in database for article {article.id}")
                    context['content_blocks_json'] = '[]'
            except Exception as e:
                logger.error(f"Error processing content blocks for edit form: {str(e)}")
                context['content_blocks_json'] = '[]'
        
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
        import logging
        import json
        logger = logging.getLogger(__name__)
        
        # Process content blocks data if provided
        content_blocks = self.request.POST.get('content_blocks')
        logger.info(f"Content blocks data received: {content_blocks[:100] if content_blocks else 'None'}...")
        
        if content_blocks:
            form.instance.content = f"Content blocks: {len(content_blocks)} characters"
            
            # Store the content blocks directly in the database JSONField
            try:
                # Validate JSON before storing
                json_data = json.loads(content_blocks)
                form.instance.content_blocks = json_data
                logger.info(f"Storing content blocks in database JSONField for article {form.instance.id or 'new'}, blocks: {len(json_data)}")
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON in content blocks: {str(e)}")
        else:
            # If no content blocks provided but we're editing an existing article with content blocks
            if hasattr(form.instance, 'id') and form.instance.id and form.instance.content_blocks:
                logger.warning(f"No content blocks provided in form, but article {form.instance.id} has existing blocks. Preserving existing blocks.")
                # Keep existing content blocks
        
        # Ensure the slug is set if not provided
        from django.utils.text import slugify
        if not form.instance.slug:
            form.instance.slug = slugify(form.instance.title)
        logger.info(f"Using slug: {form.instance.slug}")
        
        # Save the form
        try:
            self.object = form.save()
            logger.info(f"Article updated with ID: {self.object.id}, slug: {self.object.slug}")
            
            # If we didn't have the ID before (new article), update the session key
            if content_blocks and f'article_None_content_blocks' in self.request.session:
                self.request.session[f'article_{self.object.id}_content_blocks'] = self.request.session[f'article_None_content_blocks']
                del self.request.session[f'article_None_content_blocks']
                self.request.session.modified = True
                logger.info(f"Updated session key for new article {self.object.id}")
            
            # Add success message
            messages.success(self.request, f"Article '{self.object.title}' updated successfully.")
            
            # Get the absolute URL for the article
            redirect_url = self.object.get_absolute_url()
            logger.info(f"Redirecting to: {redirect_url}")
            
            # Check if this is an AJAX request
            is_ajax = self.request.headers.get('X-Requested-With') == 'XMLHttpRequest'
            logger.info(f"Is AJAX request: {is_ajax}")
            
            if is_ajax:
                # Return JSON response for AJAX requests with full URL
                # Include the full URL to avoid any client-side URL construction issues
                full_redirect_url = self.request.build_absolute_uri(redirect_url)
                logger.info(f"Full redirect URL for AJAX: {full_redirect_url}")
                
                return JsonResponse({
                    'success': True,
                    'redirect_url': full_redirect_url,
                    'slug': self.object.slug,
                    'article_id': self.object.id,
                    'message': f"Article '{self.object.title}' updated successfully."
                })
            else:
                # Use HttpResponseRedirect for standard form submissions
                from django.http import HttpResponseRedirect
                response = HttpResponseRedirect(redirect_url)
                response['X-Article-Updated'] = 'True'
                response['X-Article-Slug'] = self.object.slug
                logger.info(f"Returning HttpResponseRedirect to {redirect_url}")
                return response
        except Exception as e:
            logger.error(f"Error updating article: {str(e)}")
            # Re-raise the exception to let Django handle it
            raise


class KnowledgeArticleDeleteView(LoginRequiredMixin, BreadcrumbMixin, DeleteView):
    """View for deleting a knowledge article"""
    model = KnowledgeArticle
    template_name = 'education/knowledge/article_confirm_delete.html'
    context_object_name = 'article'
    success_url = reverse_lazy('education:knowledge_base')
    slug_url_kwarg = 'slug'
    

class TestFormView(LoginRequiredMixin, BreadcrumbMixin, TemplateView):
    """Test view for form submission"""
    template_name = 'education/knowledge/test_form.html'
    
    def get_breadcrumbs(self):
        breadcrumbs = [
            {'title': 'Education', 'url': reverse_lazy('education:dashboard')},
            {'title': 'Knowledge Base', 'url': reverse_lazy('education:knowledge_base')},
            {'title': 'Test Form', 'url': '#'}
        ]
        return breadcrumbs
    
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
