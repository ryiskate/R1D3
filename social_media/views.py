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


class SocialMediaDashboardView(LoginRequiredMixin, TemplateView):
    """Dashboard view for the Social Media department"""
    template_name = 'social_media/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_department'] = 'social_media'
        return context


class PostScheduleView(LoginRequiredMixin, TemplateView):
    """View for managing post schedules"""
    template_name = 'social_media/schedule.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_department'] = 'social_media'
        return context


class PostIdeasView(LoginRequiredMixin, TemplateView):
    """View for managing post ideas"""
    template_name = 'social_media/ideas.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_department'] = 'social_media'
        return context


class AnalyticsView(LoginRequiredMixin, TemplateView):
    """View for social media analytics"""
    template_name = 'social_media/analytics.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_department'] = 'social_media'
        return context


@method_decorator(require_POST, name='dispatch')
class SocialMediaTaskBatchUpdateView(LoginRequiredMixin, View):
    """
    View for handling batch updates to social media tasks via AJAX
    """
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            task_ids = data.get('task_ids', [])
            update_data = data.get('update_data', {})
            
            if not task_ids or not update_data:
                return JsonResponse({'success': False, 'message': 'No tasks or update data provided'}, status=400)
            
            # Filter tasks by ID and ensure they are social media tasks
            tasks = GameTask.objects.filter(id__in=task_ids, company_section='social_media')
            
            if not tasks.exists():
                return JsonResponse({'success': False, 'message': 'No valid social media tasks found'}, status=404)
            
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
                    
            if 'campaign_id' in update_data and update_data['campaign_id']:
                update_fields['campaign_id'] = update_data['campaign_id']
                
            if 'channel' in update_data and update_data['channel']:
                update_fields['channel'] = update_data['channel']
            
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

class SocialMediaTasksView(LoginRequiredMixin, ListView):
    """View for displaying social media-specific tasks in a dashboard format"""
    model = GameTask
    template_name = 'projects/social_media_task_dashboard.html'
    context_object_name = 'social_media_tasks'
    
    def get_queryset(self):
        # Filter tasks for social media section
        queryset = GameTask.objects.filter(company_section='social_media')
        
        # Apply filters from request parameters
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
            
        priority = self.request.GET.get('priority')
        if priority:
            queryset = queryset.filter(priority=priority)
            
        campaign_id = self.request.GET.get('campaign_id')
        if campaign_id:
            queryset = queryset.filter(campaign_id=campaign_id)
            
        channel = self.request.GET.get('channel')
        if channel:
            queryset = queryset.filter(channel=channel)
            
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
        context['active_department'] = 'social_media'
        
        # Get all social media tasks for statistics
        all_social_media_tasks = GameTask.objects.filter(company_section='social_media')
        
        # Task statistics by status
        total_count = all_social_media_tasks.count()
        backlog_count = all_social_media_tasks.filter(status='backlog').count()
        to_do_count = all_social_media_tasks.filter(status='to_do').count()
        in_progress_count = all_social_media_tasks.filter(status='in_progress').count()
        in_review_count = all_social_media_tasks.filter(status='in_review').count()
        done_count = all_social_media_tasks.filter(status='done').count()
        blocked_count = all_social_media_tasks.filter(status='blocked').count()
        
        # Calculate percentages (rounded to nearest 10 for CSS classes)
        def calculate_percentage(count):
            if total_count == 0:
                return 0
            percentage = (count / total_count) * 100
            # Round to nearest 10 for CSS classes
            return round(percentage / 10) * 10
        
        task_stats = {
            'total': total_count,
            'backlog': backlog_count,
            'to_do': to_do_count,
            'in_progress': in_progress_count,
            'in_review': in_review_count,
            'done': done_count,
            'blocked': blocked_count,
            # Add percentages rounded to nearest 10 for CSS classes
            'backlog_percent': calculate_percentage(backlog_count),
            'to_do_percent': calculate_percentage(to_do_count),
            'in_progress_percent': calculate_percentage(in_progress_count),
            'in_review_percent': calculate_percentage(in_review_count),
            'done_percent': calculate_percentage(done_count),
            'blocked_percent': calculate_percentage(blocked_count),
        }
        context['task_stats'] = task_stats
        
        # Get distinct campaigns from social media tasks
        campaigns = all_social_media_tasks.values('campaign_id').annotate(
            count=Count('id')
        ).order_by('campaign_id')
        
        # Format campaigns for template
        formatted_campaigns = []
        for campaign in campaigns:
            if campaign['campaign_id']:
                formatted_campaigns.append({
                    'id': campaign['campaign_id'],
                    'title': campaign['campaign_id'],
                    'count': campaign['count']
                })
        context['campaigns'] = formatted_campaigns
        
        # Get all users for assignment filter
        context['users'] = User.objects.filter(is_active=True).order_by('first_name', 'last_name')
        
        # Add today's date for due date comparisons
        context['today'] = date.today()
        
        # Count tasks by company section for navigation card
        context['social_media_tasks_count'] = all_social_media_tasks.count()
        
        # Check if filters are applied
        context['current_filters'] = any([
            self.request.GET.get('status'),
            self.request.GET.get('priority'),
            self.request.GET.get('campaign_id'),
            self.request.GET.get('channel'),
            self.request.GET.get('assigned_to'),
            self.request.GET.get('due_date_range')
        ])
        
        return context
