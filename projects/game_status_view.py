from django.views import View
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.urls import reverse

from .game_models import GameProject

class GameStatusUpdateView(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    Simple view to update a game project's status
    """
    
    def test_func(self):
        # Only staff members can update game status
        return self.request.user.is_staff
    
    def post(self, request, *args, **kwargs):
        game = get_object_or_404(GameProject, pk=kwargs.get('pk'))
        new_status = request.POST.get('status')
        
        # Validate that the status is one of the allowed choices
        valid_statuses = [status[0] for status in GameProject.STATUS_CHOICES]
        
        if new_status in valid_statuses:
            old_status = game.get_status_display()
            game.status = new_status
            game.save()
            messages.success(request, f"Game status updated from '{old_status}' to '{game.get_status_display()}'")
        else:
            messages.error(request, "Invalid status selected")
            
        return redirect('games:game_detail', pk=game.pk)
