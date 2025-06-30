from django.shortcuts import render
from django.views.generic import TemplateView, ListView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
import json
from datetime import date, timedelta

from projects.game_models import GameTask
from projects.task_models import EducationTask
from django.contrib.auth.models import User


class EducationDashboardView(LoginRequiredMixin, TemplateView):
    """Dashboard view for the Education department"""
    template_name = 'education/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_department'] = 'education'
        return context


class ClassesView(LoginRequiredMixin, TemplateView):
    """View for managing education classes"""
    template_name = 'education/classes.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_department'] = 'education'
        return context


class CourseMaterialsView(LoginRequiredMixin, TemplateView):
    """View for managing course materials"""
    template_name = 'education/materials.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_department'] = 'education'
        return context


class ScheduleView(LoginRequiredMixin, TemplateView):
    """View for class schedules"""
    template_name = 'education/schedule.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_department'] = 'education'
        return context


class EducationTasksView(LoginRequiredMixin, TemplateView):
    """View for displaying education-specific tasks in a dashboard format"""
    template_name = 'education/tasks.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_department'] = 'education'
        
        # Add today's date for template comparison
        context['today'] = date.today()
        
        # Get all education tasks
        tasks = EducationTask.objects.all()
        
        # Apply filters from query parameters
        course_id = self.request.GET.get('course_id')
        if course_id:
            tasks = tasks.filter(course_id=course_id)
            
        target_audience = self.request.GET.get('target_audience')
        if target_audience:
            tasks = tasks.filter(target_audience=target_audience)
            
        status = self.request.GET.get('status')
        if status:
            tasks = tasks.filter(status=status)
            
        priority = self.request.GET.get('priority')
        if priority:
            tasks = tasks.filter(priority=priority)
            
        # Get unique course IDs and target audiences for filters
        context['course_ids'] = EducationTask.objects.values_list('course_id', flat=True).distinct()
        context['target_audiences'] = EducationTask.objects.values_list('target_audience', flat=True).distinct()
        context['tasks'] = tasks
        context['users'] = User.objects.all()
        
        # Task statistics for status cards
        task_stats = {
            'to_do': tasks.filter(status='to_do').count(),
            'in_progress': tasks.filter(status='in_progress').count(),
            'in_review': tasks.filter(status='in_review').count(),
            'done': tasks.filter(status='done').count(),
            'backlog': tasks.filter(status='backlog').count(),
        }
        context['task_stats'] = task_stats
        context['total_tasks'] = tasks.count()
        
        return context


@method_decorator(require_POST, name='dispatch')
class EducationTaskBatchUpdateView(LoginRequiredMixin, View):
    """
    View for handling batch updates to education tasks via AJAX
    """
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            task_ids = data.get('task_ids', [])
            update_data = data.get('update_data', {})
            
            if not task_ids or not update_data:
                return JsonResponse({'success': False, 'message': 'No tasks or update data provided'}, status=400)
            
            # Filter tasks by ID and ensure they are education tasks
            tasks = GameTask.objects.filter(id__in=task_ids, company_section='education')
            
            if not tasks.exists():
                return JsonResponse({'success': False, 'message': 'No valid education tasks found'}, status=404)
            
            # Process update data
            update_fields = {}
            
            if 'status' in update_data and update_data['status']:
                update_fields['status'] = update_data['status']
                
            if 'priority' in update_data and update_data['priority']:
                update_fields['priority'] = update_data['priority']
                
            if 'assigned_to' in update_data:
                if update_data['assigned_to'] == 'unassigned':
                    update_fields['assigned_to'] = None
                elif update_data['assigned_to']:
                    try:
                        user = User.objects.get(id=update_data['assigned_to'])
                        update_fields['assigned_to'] = user
                    except User.DoesNotExist:
                        pass
                        
            if 'due_date' in update_data:
                if update_data['due_date'] == 'no_date':
                    update_fields['due_date'] = None
                elif update_data['due_date']:
                    update_fields['due_date'] = update_data['due_date']
                    
            if 'course_id' in update_data and update_data['course_id']:
                update_fields['course_id'] = update_data['course_id']
                
            if 'target_audience' in update_data and update_data['target_audience']:
                update_fields['target_audience'] = update_data['target_audience']
            
            # Apply updates
            if update_fields:
                tasks.update(**update_fields)
                
                return JsonResponse({
                    'success': True,
                    'message': f'Successfully updated {tasks.count()} tasks',
                    'updated_count': tasks.count()
                })
            else:
                return JsonResponse({'success': False, 'message': 'No valid update fields provided'}, status=400)
                
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=500)


class EducationTaskCreateView(LoginRequiredMixin, TemplateView):
    """
    View for creating new education tasks using the object-oriented EducationTask model
    """
    template_name = 'education/task_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_department'] = 'education'
        context['form'] = self.get_form()
        context['is_update'] = False
        return context
        
    def get_form(self):
        from projects.task_forms import EducationTaskForm
        return EducationTaskForm()
        
    def post(self, request, *args, **kwargs):
        from django.shortcuts import redirect
        from projects.task_forms import EducationTaskForm
        
        form = EducationTaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.created_by = request.user
            task.save()
            return redirect('education:task_detail', pk=task.pk)
        
        context = self.get_context_data()
        context['form'] = form
        return self.render_to_response(context)


class EducationTaskDetailView(LoginRequiredMixin, TemplateView):
    """
    View for displaying education task details
    """
    template_name = 'education/task_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.kwargs.get('pk')
        
        from projects.task_models import EducationTask
        from django.shortcuts import get_object_or_404
        
        task = get_object_or_404(EducationTask, pk=pk)
        context['task'] = task
        context['active_department'] = 'education'
        
        return context


class EducationTaskUpdateView(LoginRequiredMixin, TemplateView):
    """
    View for updating education tasks
    """
    template_name = 'education/task_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.kwargs.get('pk')
        
        from projects.task_models import EducationTask
        from django.shortcuts import get_object_or_404
        from projects.task_forms import EducationTaskForm
        
        task = get_object_or_404(EducationTask, pk=pk)
        form = EducationTaskForm(instance=task)
        
        context['task'] = task
        context['form'] = form
        context['active_department'] = 'education'
        context['is_update'] = True
        
        return context
        
    def post(self, request, pk, *args, **kwargs):
        from django.shortcuts import redirect, get_object_or_404
        from projects.task_models import EducationTask
        from projects.task_forms import EducationTaskForm
        
        task = get_object_or_404(EducationTask, pk=pk)
        form = EducationTaskForm(request.POST, instance=task)
        
        if form.is_valid():
            form.save()
            return redirect('education:task_detail', pk=task.pk)
        
        context = self.get_context_data()
        context['form'] = form
        return self.render_to_response(context)


class EducationTaskDeleteView(LoginRequiredMixin, View):
    """
    View for deleting education tasks
    """
    def get(self, request, pk, *args, **kwargs):
        # Import here to avoid circular imports
        from django.shortcuts import redirect, get_object_or_404
        from django.urls import reverse
        from projects.task_models import EducationTask
        
        task = get_object_or_404(EducationTask, pk=pk)
        task.delete()
        return redirect('education:tasks')


class EducationTaskStatusUpdateView(LoginRequiredMixin, View):
    """
    View for updating the status of an education task
    """
    def post(self, request, pk, *args, **kwargs):
        from django.shortcuts import redirect, get_object_or_404
        from projects.task_models import EducationTask
        
        task = get_object_or_404(EducationTask, pk=pk)
        status = request.POST.get('status')
        
        if status and status in dict(EducationTask.STATUS_CHOICES).keys():
            task.status = status
            task.save(update_fields=['status', 'updated_at'])
        
        return redirect('education:task_detail', pk=pk)


class EducationTaskHoursUpdateView(LoginRequiredMixin, View):
    """
    View for updating the actual hours of an education task
    """
    def post(self, request, pk, *args, **kwargs):
        from django.shortcuts import redirect, get_object_or_404
        from projects.task_models import EducationTask
        
        task = get_object_or_404(EducationTask, pk=pk)
        try:
            actual_hours = float(request.POST.get('actual_hours', 0))
            task.actual_hours = actual_hours
            task.save(update_fields=['actual_hours', 'updated_at'])
        except (ValueError, TypeError):
            pass  # Invalid input, just ignore
        
        return redirect('education:task_detail', pk=pk)
