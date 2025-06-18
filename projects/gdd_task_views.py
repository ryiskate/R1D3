from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.db import transaction

from .game_models import GameTask, GDDFeature

class GDDTaskStatusUpdateView(LoginRequiredMixin, View):
    """
    View to handle task status updates directly from the GDD interface
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
            
            # If this task is linked to a GDD feature, update the feature status
            if hasattr(task, 'gdd_feature') and task.gdd_feature:
                feature = task.gdd_feature
                feature.status = task.status
                feature.save()
        
        # Check if AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': updated,
                'task_id': task.pk,
                'new_status': task.status,
                'status_display': task.get_status_display(),
                'actual_hours': task.actual_hours
            })
        
        # Redirect back to the referring page or task detail page
        return redirect(request.META.get('HTTP_REFERER', f'/games/tasks/{task.pk}/'))

@method_decorator(require_POST, name='dispatch')
class BatchTaskUpdateView(LoginRequiredMixin, View):
    """
    View to handle batch updates of multiple tasks at once
    """
    def post(self, request):
        task_ids = request.POST.getlist('task_ids')
        new_status = request.POST.get('status')
        
        if not task_ids or not new_status:
            return JsonResponse({'success': False, 'error': 'Missing task IDs or status'})
        
        try:
            with transaction.atomic():
                updated_count = 0
                for task_id in task_ids:
                    try:
                        task = GameTask.objects.get(pk=task_id)
                        task.status = new_status
                        task.save()
                        
                        # Update linked feature if exists
                        if hasattr(task, 'gdd_feature') and task.gdd_feature:
                            feature = task.gdd_feature
                            feature.status = new_status
                            feature.save()
                        
                        updated_count += 1
                    except GameTask.DoesNotExist:
                        continue
                
                return JsonResponse({
                    'success': True,
                    'updated_count': updated_count,
                    'message': f"Updated {updated_count} tasks to {dict(GameTask.STATUS_CHOICES).get(new_status, new_status)}"
                })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
