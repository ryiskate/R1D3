from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from .models import QuickLink
from .forms import QuickLinkForm


class QuickLinkListView(LoginRequiredMixin, ListView):
    """View for listing user's quick links"""
    model = QuickLink
    template_name = 'core/quick_links/list.html'
    context_object_name = 'quick_links'
    
    def get_queryset(self):
        """Only return quick links for the current user"""
        return QuickLink.objects.filter(user=self.request.user)


class QuickLinkCreateView(LoginRequiredMixin, CreateView):
    """View for creating a new quick link"""
    model = QuickLink
    form_class = QuickLinkForm
    template_name = 'core/quick_links/form.html'
    success_url = reverse_lazy('core:quick_links')
    
    def form_valid(self, form):
        """Set the user to the current user"""
        form.instance.user = self.request.user
        # Set position to the next available position
        max_position = QuickLink.objects.filter(user=self.request.user).count()
        form.instance.position = max_position + 1
        return super().form_valid(form)


class QuickLinkUpdateView(LoginRequiredMixin, UpdateView):
    """View for updating an existing quick link"""
    model = QuickLink
    form_class = QuickLinkForm
    template_name = 'core/quick_links/form.html'
    success_url = reverse_lazy('core:quick_links')
    
    def get_queryset(self):
        """Only allow editing quick links owned by the current user"""
        return QuickLink.objects.filter(user=self.request.user)


class QuickLinkDeleteView(LoginRequiredMixin, DeleteView):
    """View for deleting a quick link"""
    model = QuickLink
    template_name = 'core/quick_links/confirm_delete.html'
    success_url = reverse_lazy('core:quick_links')
    
    def get_queryset(self):
        """Only allow deleting quick links owned by the current user"""
        return QuickLink.objects.filter(user=self.request.user)


def reorder_quick_links(request):
    """AJAX view for reordering quick links"""
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        link_ids = request.POST.getlist('link_ids[]')
        
        # Update positions
        for position, link_id in enumerate(link_ids, 1):
            link = get_object_or_404(QuickLink, id=link_id, user=request.user)
            link.position = position
            link.save()
            
        return JsonResponse({'status': 'success'})
    
    return JsonResponse({'status': 'error'}, status=400)
