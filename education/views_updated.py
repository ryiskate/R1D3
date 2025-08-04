from django.shortcuts import render
from django.views.generic import TemplateView, ListView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.urls import reverse
import json
from datetime import date, timedelta

from core.mixins import BreadcrumbMixin

from projects.game_models import GameTask
from projects.task_models import EducationTask
from django.contrib.auth.models import User
from education.course.models import Course


class EducationDashboardView(LoginRequiredMixin, TemplateView):
    """Dashboard view for the Education department"""
    template_name = 'education/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_department'] = 'education'
        
        # Fetch real data for dashboard statistics
        
        # 1. Active Classes - Count published courses
        active_courses = Course.objects.filter(status='published').count()
        context['active_classes_count'] = active_courses
        
        # 2. Students Enrolled - Count all users (simplified approach)
        # In a real system, you might have a specific Student model or a way to identify users as students
        students_count = User.objects.count()
        context['students_enrolled_count'] = students_count
        
        # 3. Course Completion - Calculate average completion percentage
        # This is a simplified approach. In a real system, you might track student progress per course
        all_tasks = EducationTask.objects.all()
        completed_tasks = all_tasks.filter(status='done').count()
        total_tasks = all_tasks.count()
        
        if total_tasks > 0:
            completion_percentage = int((completed_tasks / total_tasks) * 100)
        else:
            completion_percentage = 0
            
        context['course_completion_percentage'] = completion_percentage
        
        # 4. Pending Tasks - Count tasks that are not done
        pending_tasks = EducationTask.objects.filter(
            ~Q(status='done')
        ).count()
        context['pending_tasks_count'] = pending_tasks
        
        # Fetch only the current user's education tasks
        user_tasks = EducationTask.objects.filter(assigned_to=self.request.user).order_by('-due_date')
        context['user_education_tasks'] = user_tasks
        
        return context
