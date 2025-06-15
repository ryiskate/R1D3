from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

from .game_models import GameTask

class TaskStatusUpdateView(LoginRequiredMixin, View):
    """
    View to handle direct status updates and hours logging from the task detail page
    """
    def post(self, request, pk):
        task = get_object_or_404(GameTask, pk=pk)
        updated = False
        
        # Update the task status
        if 'status' in request.POST:
            task.status = request.POST.get('status')
            updated = True
            messages.success(request, f"Task status updated to {task.get_status_display()}")
            
        # Update actual hours
        if 'actual_hours' in request.POST:
            try:
                actual_hours = float(request.POST.get('actual_hours'))
                task.actual_hours = actual_hours
                updated = True
                messages.success(request, f"Task hours updated to {actual_hours}")
            except ValueError:
                messages.error(request, "Invalid hours value provided")
        
        # Save the task if any updates were made
        if updated:
            task.save()
        
        # Redirect back to the task detail page
        return redirect('games:task_detail', pk=task.pk)
