from django.shortcuts import render, get_object_or_404
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.db.models import Q
import json

from .game_models import GameTask, GameProject

class GameTaskStatusUpdateView(LoginRequiredMixin, View):
    """
    Update task status via AJAX
    """
    @method_decorator(require_POST)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request, pk):
        task = get_object_or_404(GameTask, pk=pk)
        
        # Check if user has permission to update this task
        if not (request.user.is_staff or 
                request.user == task.assigned_to or 
                request.user == task.game.lead_developer or
                request.user == task.game.lead_designer or
                request.user == task.game.lead_artist or
                request.user in task.game.team_members.all()):
            return JsonResponse({
                'success': False,
                'message': 'You do not have permission to update this task'
            }, status=403)
        
        # Update task status
        if 'status' in request.POST:
            old_status = task.status
            new_status = request.POST.get('status')
            
            # Validate status
            valid_statuses = [status[0] for status in GameTask.STATUS_CHOICES]
            if new_status not in valid_statuses:
                return JsonResponse({
                    'success': False,
                    'message': 'Invalid status'
                }, status=400)
            
            task.status = new_status
            task.save()
            
            # Return success response
            return JsonResponse({
                'success': True,
                'message': f'Task status updated from {old_status} to {new_status}',
                'task_id': task.id,
                'new_status': new_status
            })
        
        # If we get here, no valid update parameters were provided
        return JsonResponse({
            'success': False,
            'message': 'No valid update parameters provided'
        }, status=400)


class GameTaskHoursUpdateView(LoginRequiredMixin, View):
    """
    Update task actual hours via AJAX
    """
    @method_decorator(require_POST)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request, pk):
        task = get_object_or_404(GameTask, pk=pk)
        
        # Check if user has permission to update this task
        if not (request.user.is_staff or 
                request.user == task.assigned_to or 
                request.user == task.game.lead_developer or
                request.user == task.game.lead_designer or
                request.user == task.game.lead_artist or
                request.user in task.game.team_members.all()):
            return JsonResponse({
                'success': False,
                'message': 'You do not have permission to update this task'
            }, status=403)
        
        # Update task hours
        if 'actual_hours' in request.POST:
            try:
                actual_hours = float(request.POST.get('actual_hours'))
                if actual_hours < 0:
                    raise ValueError("Hours cannot be negative")
                
                task.actual_hours = actual_hours
                task.save()
                
                # Return success response
                return JsonResponse({
                    'success': True,
                    'message': f'Task hours updated to {actual_hours}',
                    'task_id': task.id,
                    'actual_hours': actual_hours
                })
            except ValueError as e:
                return JsonResponse({
                    'success': False,
                    'message': f'Invalid hours value: {str(e)}'
                }, status=400)
        
        # If we get here, no valid update parameters were provided
        return JsonResponse({
            'success': False,
            'message': 'No valid update parameters provided'
        }, status=400)


class GameTaskBatchUpdateView(LoginRequiredMixin, View):
    """
    Update multiple tasks at once via AJAX
    """
    @method_decorator(require_POST)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request):
        try:
            # Parse JSON data from request body
            data = json.loads(request.body)
            task_ids = data.get('task_ids', [])
            status = data.get('status')
            
            if not task_ids:
                return JsonResponse({
                    'success': False,
                    'message': 'No tasks specified'
                }, status=400)
            
            if not status:
                return JsonResponse({
                    'success': False,
                    'message': 'No status specified'
                }, status=400)
            
            # Validate status
            valid_statuses = [status_choice[0] for status_choice in GameTask.STATUS_CHOICES]
            if status not in valid_statuses:
                return JsonResponse({
                    'success': False,
                    'message': 'Invalid status'
                }, status=400)
            
            # Get tasks and check permissions
            tasks = GameTask.objects.filter(id__in=task_ids)
            
            # Filter to only tasks the user can update
            if not request.user.is_staff:
                tasks = tasks.filter(
                    Q(assigned_to=request.user) | 
                    Q(game__lead_developer=request.user) |
                    Q(game__lead_designer=request.user) |
                    Q(game__lead_artist=request.user) |
                    Q(game__team_members=request.user)
                ).distinct()
            
            if not tasks:
                return JsonResponse({
                    'success': False,
                    'message': 'No tasks found or you do not have permission to update them'
                }, status=403)
            
            # Update tasks
            updated_count = tasks.update(status=status)
            
            # Return success response
            return JsonResponse({
                'success': True,
                'message': f'Updated {updated_count} tasks to {status}',
                'updated_count': updated_count,
                'new_status': status
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': 'Invalid JSON data'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error updating tasks: {str(e)}'
            }, status=500)
