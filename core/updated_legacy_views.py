"""
Updated legacy views for backward compatibility that use the model_utils module.
"""
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from django.http import Http404

# Import model utilities
from .model_utils import get_task_model_map


class R1D3TaskDetailLegacyView(LoginRequiredMixin, View):
    """
    Legacy view for backward compatibility.
    Determines the task type and redirects to the new URL pattern.
    """
    def get(self, request, pk):
        # Get the model map from the utility function
        task_models = get_task_model_map()
        
        for task_type, model in task_models.items():
            try:
                task = model.objects.get(pk=pk)
                # Redirect to the new URL pattern with task_type
                return redirect('core:r1d3_task_detail', task_type=task_type, pk=pk)
            except model.DoesNotExist:
                continue
        
        # If no task found in any model
        raise Http404(f"No task found with ID {pk}")


class R1D3TaskUpdateLegacyView(LoginRequiredMixin, View):
    """
    Legacy view for backward compatibility.
    Determines the task type and redirects to the new URL pattern.
    """
    def get(self, request, pk):
        # Get the model map from the utility function
        task_models = get_task_model_map()
        
        for task_type, model in task_models.items():
            try:
                task = model.objects.get(pk=pk)
                # Redirect to the new URL pattern with task_type
                return redirect('core:r1d3_task_update', task_type=task_type, pk=pk)
            except model.DoesNotExist:
                continue
        
        # If no task found in any model
        raise Http404(f"No task found with ID {pk}")


class R1D3TaskDeleteLegacyView(LoginRequiredMixin, View):
    """
    Legacy view for backward compatibility.
    Determines the task type and redirects to the new URL pattern.
    """
    def get(self, request, pk):
        # Get the model map from the utility function
        task_models = get_task_model_map()
        
        for task_type, model in task_models.items():
            try:
                task = model.objects.get(pk=pk)
                # Redirect to the new URL pattern with task_type
                return redirect('core:r1d3_task_delete', task_type=task_type, pk=pk)
            except model.DoesNotExist:
                continue
        
        # If no task found in any model
        raise Http404(f"No task found with ID {pk}")
