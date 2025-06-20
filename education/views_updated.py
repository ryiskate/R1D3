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
    model = GameTask
    template_name = 'projects/education_task_dashboard_enhanced.html'
    context_object_name = 'education_tasks'
    
    def get_queryset(self):
        # Filter tasks for education section
        queryset = GameTask.objects.filter(company_section='education')
        
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
        context['active_department'] = 'education'
        
        # Get all education tasks for statistics
        all_education_tasks = GameTask.objects.filter(company_section='education')
        
        # Task statistics by status
        task_stats = {
            'total': all_education_tasks.count(),
            'backlog': all_education_tasks.filter(status='backlog').count(),
            'to_do': all_education_tasks.filter(status='to_do').count(),
            'in_progress': all_education_tasks.filter(status='in_progress').count(),
            'in_review': all_education_tasks.filter(status='in_review').count(),
            'done': all_education_tasks.filter(status='done').count(),
            'blocked': all_education_tasks.filter(status='blocked').count(),
        }
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
