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


class EducationTasksView(LoginRequiredMixin, ListView):
    """View for displaying education-specific tasks in a dashboard format"""
    model = EducationTask
    template_name = 'education/tasks.html'
    context_object_name = 'tasks'  # Changed to match template expectations
    
    def get(self, request, *args, **kwargs):
        print("DEBUG: education.views.EducationTasksView is being called")
        return super().get(request, *args, **kwargs)
    
    def get_queryset(self):
        print("DEBUG: Starting EducationTasksView.get_queryset()")
        # Get all education tasks
        queryset = EducationTask.objects.all()
        print(f"DEBUG: Initial queryset count: {queryset.count()}")
        
        # Apply filters from request parameters
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
            print(f"DEBUG: After status filter '{status}': {queryset.count()} tasks")
            
        priority = self.request.GET.get('priority')
        if priority:
            queryset = queryset.filter(priority=priority)
            print(f"DEBUG: After priority filter '{priority}': {queryset.count()} tasks")
            
        course_id = self.request.GET.get('course_id')
        if course_id:
            queryset = queryset.filter(course_id=course_id)
            print(f"DEBUG: After course_id filter '{course_id}': {queryset.count()} tasks")
            
        target_audience = self.request.GET.get('target_audience')
        if target_audience:
            queryset = queryset.filter(target_audience=target_audience)
            print(f"DEBUG: After target_audience filter '{target_audience}': {queryset.count()} tasks")
            
        assigned_to = self.request.GET.get('assigned_to')
        if assigned_to:
            if assigned_to == 'unassigned':
                queryset = queryset.filter(assigned_to__isnull=True)
                print(f"DEBUG: After assigned_to filter 'unassigned': {queryset.count()} tasks")
            else:
                queryset = queryset.filter(assigned_to_id=assigned_to)
                print(f"DEBUG: After assigned_to filter '{assigned_to}': {queryset.count()} tasks")
        
        # Apply due date filtering
        queryset = self.apply_due_date_filter(queryset)
        print(f"DEBUG: After due date filtering: {queryset.count()} tasks")
        
        print(f"DEBUG: Final queryset count: {queryset.count()} education tasks")
        for task in queryset[:3]:
            print(f"DEBUG: Task {task.id}: {task.title} (Status: {task.status})")
                
        return queryset
    
    # Removed create_sample_education_tasks method as we're now using EducationTask model directly
    
    def apply_due_date_filter(self, queryset):
        due_date_range = self.request.GET.get('due_date_range')
        today = date.today()
        if due_date_range:
            if due_date_range == 'overdue':
                queryset = queryset.filter(due_date__lt=today)
            elif due_date_range == 'today':
                queryset = queryset.filter(due_date=today)
            elif due_date_range == 'tomorrow':
                tomorrow = today + timedelta(days=1)
                queryset = queryset.filter(due_date=tomorrow)
            elif due_date_range == 'this_week':
                # Get the start and end of the current week
                start_of_week = today - timedelta(days=today.weekday())
                end_of_week = start_of_week + timedelta(days=6)
                queryset = queryset.filter(due_date__gte=start_of_week, due_date__lte=end_of_week)
            elif due_date_range == 'next_week':
                # Get the start and end of next week
                start_of_next_week = today + timedelta(days=(7 - today.weekday()))
                end_of_next_week = start_of_next_week + timedelta(days=6)
                queryset = queryset.filter(due_date__gte=start_of_next_week, due_date__lte=end_of_next_week)
            elif due_date_range == 'no_date':
                queryset = queryset.filter(due_date__isnull=True)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        print("DEBUG: Starting EducationTasksView.get_context_data()")
        context = super().get_context_data(**kwargs)
        print(f"DEBUG: Context after super(): {list(context.keys())}")
        
        # Get all education tasks for statistics
        all_education_tasks = EducationTask.objects.all()
        print(f"DEBUG: Found {all_education_tasks.count()} total education tasks for stats")
        
        # Calculate task statistics
        task_stats = {
            'total': all_education_tasks.count(),
            'to_do': all_education_tasks.filter(status='to_do').count(),
            'in_progress': all_education_tasks.filter(status='in_progress').count(),
            'in_review': all_education_tasks.filter(status='in_review').count(),
            'done': all_education_tasks.filter(status='done').count(),
            'backlog': all_education_tasks.filter(status='backlog').count(),
            'blocked': all_education_tasks.filter(status='blocked').count(),
        }
        
        # Add task statistics to context
        context['task_stats'] = task_stats
        print(f"DEBUG: Task stats: {task_stats}")
        
        # Get unique course IDs for filtering
        course_ids = all_education_tasks.values_list('course_id', flat=True).distinct()
        context['course_ids'] = course_ids
        print(f"DEBUG: Unique course IDs: {list(course_ids)}")
        
        # Get unique target audiences for filtering
        target_audiences = all_education_tasks.values_list('target_audience', flat=True).distinct()
        context['target_audiences'] = target_audiences
        print(f"DEBUG: Unique target audiences: {list(target_audiences)}")
        
        # Check if tasks are in the context
        if 'tasks' in context:
            print(f"DEBUG: Tasks in context: {len(context['tasks'])}")
            if context['tasks']:
                print(f"DEBUG: First task in context: {context['tasks'][0].id} - {context['tasks'][0].title}")
        else:
            print("DEBUG: No 'tasks' in context!")
        
        # Final context keys
        print(f"DEBUG: Final context keys: {list(context.keys())}")
        
        # Get distinct courses from education tasks
        courses = all_education_tasks.values('course_id').annotate(
            count=Count('id')
        ).order_by('course_id')
        
        # Format courses for template
        formatted_courses = []
        for course in courses:
            if course['course_id']:
                formatted_courses.append({
                    'id': course['course_id'],
                    'title': course['course_id'],
                    'count': course['count']
                })
        context['courses'] = formatted_courses
        
        # Get all users for assignment filter
        context['users'] = User.objects.filter(is_active=True).order_by('first_name', 'last_name')
        
        # Add today's date for due date comparisons
        context['today'] = date.today()
        
        # Count tasks by company section for navigation card
        context['education_tasks_count'] = all_education_tasks.count()
        
        # Check if filters are applied
        context['current_filters'] = any([
            self.request.GET.get('status'),
            self.request.GET.get('priority'),
            self.request.GET.get('course_id'),
            self.request.GET.get('target_audience'),
            self.request.GET.get('assigned_to'),
            self.request.GET.get('due_date_range')
        ])
        
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


class EducationTaskCreateView(LoginRequiredMixin, View):
    """
    View for creating new education tasks using the object-oriented EducationTask model
    """
    def get(self, request, *args, **kwargs):
        # Import here to avoid circular imports
        from django.shortcuts import redirect
        from django.urls import reverse
        
        # Redirect to the proper object-oriented education task create view in the projects app
        # This ensures we're using the proper EducationTask model and form
        return redirect(reverse('projects:education_task_create'))


class EducationTaskDetailView(LoginRequiredMixin, View):
    """
    View for displaying education task details
    """
    def get(self, request, pk, *args, **kwargs):
        # Import here to avoid circular imports
        from django.shortcuts import redirect
        from django.urls import reverse
        
        # Redirect to the proper object-oriented education task detail view in the projects app
        return redirect(reverse('projects:education_task_detail', kwargs={'pk': pk}))


class EducationTaskUpdateView(LoginRequiredMixin, View):
    """
    View for updating education tasks
    """
    def get(self, request, pk, *args, **kwargs):
        # Import here to avoid circular imports
        from django.shortcuts import redirect
        from django.urls import reverse
        
        # Redirect to the proper object-oriented education task update view in the projects app
        return redirect(reverse('projects:education_task_update', kwargs={'pk': pk}))


class EducationTaskDeleteView(LoginRequiredMixin, View):
    """
    View for deleting education tasks
    """
    def get(self, request, pk, *args, **kwargs):
        # Import here to avoid circular imports
        from django.shortcuts import redirect
        from django.urls import reverse
        
        # Redirect to the proper object-oriented education task delete view in the projects app
        return redirect(reverse('projects:education_task_delete', kwargs={'pk': pk}))
