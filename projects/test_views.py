"""
Test views for debugging purposes.
"""
from django.views.generic import TemplateView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .task_forms import EducationTaskForm
from .task_models import EducationTask


class TestR1D3ButtonView(LoginRequiredMixin, TemplateView):
    """
    Simple view to test the R1D3 task creation button.
    """
    template_name = 'projects/test_r1d3_button.html'


class DebugButtonView(TemplateView):
    """
    A debug view to test different button implementations and identify redirect issues.
    """
    template_name = 'projects/debug_button.html'


class TestEducationTaskFormView(CreateView):
    """
    Test view for the education task form without authentication.
    This is for debugging template issues only.
    """
    model = EducationTask
    form_class = EducationTaskForm
    template_name = 'projects/education_task_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['section_name'] = 'Education Task'
        context['is_update'] = False
        return context
