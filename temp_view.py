
from education.course.models import Course
from projects.task_models import EducationTask

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
