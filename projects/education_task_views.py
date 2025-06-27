from django.views.generic import ListView, View, DetailView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count, Q
from django.utils import timezone
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
import json
from datetime import date, timedelta

from .task_models import EducationTask
from .task_forms import EducationTaskForm
from .game_models import GameTask  # Keep for backwards compatibility during transition
from django.contrib.auth.models import User

class EducationTaskDashboardView(LoginRequiredMixin, ListView):
    """
    View for displaying education-specific tasks in a dashboard format
    """
    model = EducationTask
    template_name = 'education/tasks.html'
    context_object_name = 'education_tasks'
    
    def get_queryset(self):
        # Create some sample education tasks if none exist
        self.create_sample_education_tasks()
        
        # Use the EducationTask model directly - no need to filter by company_section
        queryset = EducationTask.objects.all()
        
        # Apply filters from request parameters
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
            
        priority = self.request.GET.get('priority')
        if priority:
            queryset = queryset.filter(priority=priority)
            
        course_id = self.request.GET.get('course_id')
        if course_id:
            queryset = queryset.filter(course_id=course_id)
            
        target_audience = self.request.GET.get('target_audience')
        if target_audience:
            queryset = queryset.filter(target_audience=target_audience)
            
        assigned_to = self.request.GET.get('assigned_to')
        if assigned_to:
            if assigned_to == 'unassigned':
                queryset = queryset.filter(assigned_to__isnull=True)
            else:
                queryset = queryset.filter(assigned_to_id=assigned_to)
                
        return queryset
        
    def create_sample_education_tasks(self):
        """Create sample education tasks if none exist"""
        from django.contrib.auth.models import User
        
        # Check if we already have education tasks
        if EducationTask.objects.exists():
            return
            
        # Get the first user as the assignee
        user = User.objects.first()
        if not user:
            return
            
        # Create sample education tasks
        education_tasks = [
            {
                'title': 'Develop Game Design Curriculum',
                'description': 'Create a comprehensive curriculum for teaching game design principles',
                'status': 'to_do',
                'priority': 'critical',
                'course_id': 'EDU-001',
                'learning_objective': 'Master game design fundamentals',
                'target_audience': 'Beginners',
                'due_date': '2025-06-30'
            },
            {
                'title': 'Create Unity Tutorial Series',
                'description': 'Develop a series of video tutorials for Unity game development',
                'status': 'to_do',
                'priority': 'high',
                'course_id': 'EDU-002',
                'learning_objective': 'Learn Unity basics',
                'target_audience': 'Intermediate developers',
                'due_date': '2025-07-15'
            },
            {
                'title': 'Schedule Guest Lecturer',
                'description': 'Coordinate with industry professionals for guest lectures',
                'status': 'done',
                'priority': 'medium',
                'course_id': 'EDU-003',
                'learning_objective': 'Industry insights',
                'target_audience': 'All students',
                'due_date': '2025-06-10'
            },
            {
                'title': 'Update Learning Management System',
                'description': 'Implement new features in the LMS for better tracking',
                'status': 'in_progress',
                'priority': 'high',
                'course_id': 'EDU-004',
                'learning_objective': 'Improve learning analytics',
                'target_audience': 'Faculty',
                'due_date': '2025-07-05'
            },
            {
                'title': 'Prepare Student Showcase',
                'description': 'Organize end-of-term student project showcase event',
                'status': 'to_do',
                'priority': 'medium',
                'course_id': 'EDU-005',
                'learning_objective': 'Portfolio development',
                'target_audience': 'Advanced students',
                'due_date': '2025-08-20'
            }
        ]
        
        from datetime import datetime
        
        # Create the tasks
        for task_data in education_tasks:
            due_date = datetime.strptime(task_data['due_date'], '%Y-%m-%d').date() if task_data.get('due_date') else None
            
            EducationTask.objects.create(
                title=task_data['title'],
                description=task_data['description'],
                status=task_data['status'],
                priority=task_data['priority'],
                course_id=task_data['course_id'],
                learning_objective=task_data['learning_objective'],
                target_audience=task_data['target_audience'],
                assigned_to=user,
                created_by=user,
                due_date=due_date
            )
                
        due_date_range = self.request.GET.get('due_date_range')
        today = date.today()
        if due_date_range:
            if due_date_range == 'overdue':
                queryset = queryset.filter(due_date__lt=today)
            elif due_date_range == 'today':
                queryset = queryset.filter(due_date=today)
            elif due_date_range == 'this_week':
                end_of_week = today + timedelta(days=(6 - today.weekday()))
                queryset = queryset.filter(due_date__gte=today, due_date__lte=end_of_week)
            elif due_date_range == 'next_week':
                start_of_next_week = today + timedelta(days=(7 - today.weekday()))
                end_of_next_week = start_of_next_week + timedelta(days=6)
                queryset = queryset.filter(due_date__gte=start_of_next_week, due_date__lte=end_of_next_week)
            elif due_date_range == 'this_month':
                next_month = today.replace(day=28) + timedelta(days=4)
                end_of_month = next_month - timedelta(days=next_month.day)
                queryset = queryset.filter(due_date__gte=today, due_date__lte=end_of_month)
            elif due_date_range == 'no_date':
                queryset = queryset.filter(due_date__isnull=True)
        
        return queryset.order_by('status', '-priority', 'due_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get all education tasks for statistics using the new EducationTask model directly
        all_education_tasks = EducationTask.objects.all()
        total_tasks = all_education_tasks.count() or 1  # Avoid division by zero
        
        # Task statistics by status with percentage calculations
        task_stats = {}
        for status_code, status_name in self.model.STATUS_CHOICES:
            count = all_education_tasks.filter(status=status_code).count()
            task_stats[status_code] = count
            # Calculate percentage for progress bars and format as CSS-compatible string
            task_stats[f'{status_code}_percent'] = f'{int((count / total_tasks) * 100)}%'
        
        task_stats['total'] = total_tasks
        context['task_stats'] = task_stats
        
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


class EducationTaskDetailView(LoginRequiredMixin, DetailView):
    """
    View details of a specific education task
    """
    model = EducationTask
    template_name = 'projects/task_detail.html'
    context_object_name = 'task'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = self.model.STATUS_CHOICES
        context['priority_choices'] = self.model.PRIORITY_CHOICES
        context['today'] = date.today()
        
        # Get course-specific information if available
        if hasattr(self.object, 'course_id') and self.object.course_id:
            context['course_id'] = self.object.course_id
        
        # Get target audience information if available
        if hasattr(self.object, 'target_audience') and self.object.target_audience:
            context['target_audience'] = self.object.target_audience
        
        # Get related tasks
        if hasattr(self.object, 'related_tasks') and self.object.related_tasks.exists():
            context['related_tasks'] = self.object.related_tasks.all()
        
        # Get task comments
        if hasattr(self.object, 'comments'):
            context['comments'] = self.object.comments.order_by('-created_at')
        
        return context


class EducationTaskDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Delete an education task
    """
    model = EducationTask
    template_name = 'projects/task_confirm_delete.html'
    context_object_name = 'task'
    
    def test_func(self):
        # Only allow task deletion by staff or the task creator
        user = self.request.user
        task = self.get_object()
        return user.is_staff or user == task.created_by
    
    def get_success_url(self):
        messages.success(self.request, f"Task '{self.object.title}' deleted successfully!")
        return reverse_lazy('projects:education_task_dashboard')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['today'] = date.today()
        return context





class EducationTaskStatusUpdateView(LoginRequiredMixin, View):
    """
    Update the status of an education task via AJAX
    """
    @method_decorator(require_POST)
    def post(self, request, *args, **kwargs):
        task_id = request.POST.get('task_id')
        new_status = request.POST.get('status')
        
        if not task_id or not new_status:
            return JsonResponse({'status': 'error', 'message': 'Task ID and status are required'})
        
        try:
            task = EducationTask.objects.get(id=task_id)
            
            # Check if status is valid
            valid_statuses = [status[0] for status in EducationTask.STATUS_CHOICES]
            if new_status not in valid_statuses:
                return JsonResponse({'status': 'error', 'message': 'Invalid status'})
            
            # Update status
            task.status = new_status
            task.save()
            
            return JsonResponse({
                'status': 'success',
                'message': f'Task status updated to {dict(EducationTask.STATUS_CHOICES)[new_status]}',
                'new_status': new_status
            })
        except EducationTask.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Task not found'})


class EducationTaskHoursUpdateView(LoginRequiredMixin, View):
    """
    Update the actual hours of an education task via AJAX
    """
    @method_decorator(require_POST)
    def post(self, request, *args, **kwargs):
        task_id = request.POST.get('task_id')
        hours = request.POST.get('hours')
        
        if not task_id or hours is None:
            return JsonResponse({'status': 'error', 'message': 'Task ID and hours are required'})
        
        try:
            hours = float(hours)
            if hours < 0:
                return JsonResponse({'status': 'error', 'message': 'Hours cannot be negative'})
                
            task = EducationTask.objects.get(id=task_id)
            task.actual_hours = hours
            task.save()
            
            return JsonResponse({
                'status': 'success',
                'message': f'Task hours updated to {hours}',
                'hours': hours
            })
        except ValueError:
            return JsonResponse({'status': 'error', 'message': 'Invalid hours value'})
        except EducationTask.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Task not found'})


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
