/**
 * Game Task Manager JavaScript
 * Handles task filtering, status updates, batch operations, and notifications
 */
document.addEventListener('DOMContentLoaded', function() {
    // Task filtering
    const filterStatusBadges = document.querySelectorAll('.filter-status');
    if (filterStatusBadges) {
        filterStatusBadges.forEach(badge => {
            badge.addEventListener('click', function() {
                const status = this.dataset.status;
                filterTasks(status);
            });
        });
    }

    // Task status update forms
    const taskStatusForms = document.querySelectorAll('.task-status-form');
    if (taskStatusForms) {
        taskStatusForms.forEach(form => {
            form.addEventListener('change', function() {
                updateTaskStatus(this);
            });
        });
    }

    // Task hours update forms
    const taskHoursForms = document.querySelectorAll('.task-hours-form');
    if (taskHoursForms) {
        taskHoursForms.forEach(form => {
            form.addEventListener('change', function() {
                updateTaskHours(this);
            });
        });
    }

    // Batch selection checkboxes
    const taskCheckboxes = document.querySelectorAll('.task-checkbox');
    if (taskCheckboxes) {
        taskCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', function() {
                updateSelectedTasksCount();
            });
        });
    }

    // Select all checkbox
    const selectAllCheckbox = document.getElementById('selectAllTasks');
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function() {
            const isChecked = this.checked;
            document.querySelectorAll('.task-checkbox').forEach(cb => {
                cb.checked = isChecked;
            });
            updateSelectedTasksCount();
        });
    }

    // Batch update form submission
    const batchUpdateForm = document.getElementById('batchUpdateForm');
    if (batchUpdateForm) {
        batchUpdateForm.addEventListener('submit', function(e) {
            e.preventDefault();
            submitBatchUpdate();
        });
    }

    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});

/**
 * Filter tasks by status
 */
function filterTasks(status) {
    // Update active status in filter badges
    document.querySelectorAll('.filter-status').forEach(badge => {
        badge.classList.remove('active');
    });
    
    if (status) {
        document.querySelector(`.filter-status[data-status="${status}"]`).classList.add('active');
    } else {
        document.querySelector('.filter-status[data-status="all"]').classList.add('active');
    }
    
    // Show/hide tasks based on status
    const taskRows = document.querySelectorAll('.task-row');
    taskRows.forEach(row => {
        if (!status || status === 'all' || row.dataset.status === status) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}

/**
 * Update task status via AJAX
 */
function updateTaskStatus(form) {
    const taskId = form.dataset.taskId;
    const statusSelect = form.querySelector('.task-status-select');
    const status = statusSelect.value;
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    // Disable the select while updating
    statusSelect.disabled = true;
    
    fetch(`/games/tasks/${taskId}/update_status/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': csrfToken
        },
        body: `status=${status}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update task row status data attribute
            const taskRow = document.querySelector(`.task-row[data-task-id="${taskId}"]`);
            if (taskRow) {
                taskRow.dataset.status = status;
            }
            
            // Show success toast
            showToast('Success', data.message, 'success');
        } else {
            // Show error toast and reset select
            showToast('Error', data.message || 'Failed to update task status', 'danger');
            statusSelect.value = statusSelect.dataset.originalValue;
        }
    })
    .catch(error => {
        console.error('Error updating task status:', error);
        showToast('Error', 'Failed to update task status', 'danger');
        statusSelect.value = statusSelect.dataset.originalValue;
    })
    .finally(() => {
        // Re-enable the select
        statusSelect.disabled = false;
    });
}

/**
 * Update task hours via AJAX
 */
function updateTaskHours(form) {
    const taskId = form.dataset.taskId;
    const hoursInput = form.querySelector('.task-hours-input');
    const hours = hoursInput.value;
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    // Disable the input while updating
    hoursInput.disabled = true;
    
    fetch(`/games/tasks/${taskId}/update_hours/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': csrfToken
        },
        body: `actual_hours=${hours}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Show success toast
            showToast('Success', data.message, 'success');
        } else {
            // Show error toast and reset input
            showToast('Error', data.message || 'Failed to update task hours', 'danger');
            hoursInput.value = hoursInput.dataset.originalValue;
        }
    })
    .catch(error => {
        console.error('Error updating task hours:', error);
        showToast('Error', 'Failed to update task hours', 'danger');
        hoursInput.value = hoursInput.dataset.originalValue;
    })
    .finally(() => {
        // Re-enable the input
        hoursInput.disabled = false;
    });
}

/**
 * Update selected tasks count for batch operations
 */
function updateSelectedTasksCount() {
    const selectedCount = document.querySelectorAll('.task-checkbox:checked').length;
    const countBadge = document.getElementById('selectedTasksCount');
    const submitButton = document.getElementById('batchUpdateSubmit');
    
    if (countBadge) {
        countBadge.textContent = selectedCount;
    }
    
    if (submitButton) {
        submitButton.disabled = selectedCount === 0;
    }
}

/**
 * Submit batch update for selected tasks
 */
function submitBatchUpdate() {
    const selectedTaskIds = Array.from(document.querySelectorAll('.task-checkbox:checked'))
        .map(checkbox => checkbox.value);
    
    if (selectedTaskIds.length === 0) {
        showToast('Warning', 'No tasks selected', 'warning');
        return;
    }
    
    const status = document.getElementById('batchStatus').value;
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    // Disable form elements during submission
    document.getElementById('batchStatus').disabled = true;
    document.getElementById('batchUpdateSubmit').disabled = true;
    
    fetch('/games/tasks/batch_update/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({
            task_ids: selectedTaskIds,
            status: status
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update task rows with new status
            selectedTaskIds.forEach(taskId => {
                const taskRow = document.querySelector(`.task-row[data-task-id="${taskId}"]`);
                if (taskRow) {
                    taskRow.dataset.status = status;
                    const statusSelect = taskRow.querySelector('.task-status-select');
                    if (statusSelect) {
                        statusSelect.value = status;
                    }
                }
            });
            
            // Show success toast
            showToast('Success', data.message, 'success');
            
            // Close the modal
            const batchModal = bootstrap.Modal.getInstance(document.getElementById('batchUpdateModal'));
            if (batchModal) {
                batchModal.hide();
            }
            
            // Uncheck all checkboxes
            document.querySelectorAll('.task-checkbox').forEach(cb => {
                cb.checked = false;
            });
            document.getElementById('selectAllTasks').checked = false;
            updateSelectedTasksCount();
        } else {
            // Show error toast
            showToast('Error', data.message || 'Failed to update tasks', 'danger');
        }
    })
    .catch(error => {
        console.error('Error updating tasks:', error);
        showToast('Error', 'Failed to update tasks', 'danger');
    })
    .finally(() => {
        // Re-enable form elements
        document.getElementById('batchStatus').disabled = false;
        document.getElementById('batchUpdateSubmit').disabled = false;
    });
}

/**
 * Show toast notification
 */
function showToast(title, message, type) {
    const toastContainer = document.getElementById('toastContainer');
    if (!toastContainer) return;
    
    const toastId = 'toast-' + Date.now();
    const toastHtml = `
        <div id="${toastId}" class="toast align-items-center text-white bg-${type}" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="d-flex">
                <div class="toast-body">
                    <strong>${title}:</strong> ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        </div>
    `;
    
    toastContainer.insertAdjacentHTML('beforeend', toastHtml);
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement, { autohide: true, delay: 5000 });
    toast.show();
    
    // Remove toast from DOM after it's hidden
    toastElement.addEventListener('hidden.bs.toast', function() {
        toastElement.remove();
    });
}
