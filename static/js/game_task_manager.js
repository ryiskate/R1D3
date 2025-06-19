/**
 * Game Task Manager JavaScript
 * Handles task filtering, status updates, batch operations, and notifications
 * Updated to match global_task_manager.js functionality
 */
console.log('Game Task Manager JS loaded');
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM fully loaded');
    // Initialize tooltips
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    if (tooltipTriggerList.length > 0) {
        console.log('Initializing tooltips:', tooltipTriggerList.length);
        try {
            tooltipTriggerList.forEach(tooltipTriggerEl => {
                new bootstrap.Tooltip(tooltipTriggerEl);
            });
        } catch (error) {
            console.error('Error initializing tooltips:', error);
        }
    }

    // Task filtering by status badges
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
            const select = form.querySelector('.task-status-select');
            if (select) {
                select.addEventListener('change', function() {
                    updateTaskStatus(form);
                });
            }
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
    const submitBatchUpdateBtn = document.getElementById('submitBatchUpdate');
    if (submitBatchUpdateBtn) {
        submitBatchUpdateBtn.addEventListener('click', function() {
            submitBatchUpdate();
        });
    }

    // Filter form handlers
    const applyFiltersBtn = document.getElementById('applyFilters');
    if (applyFiltersBtn) {
        applyFiltersBtn.addEventListener('click', function() {
            document.getElementById('filterForm').submit();
        });
    }

    const clearFiltersBtn = document.getElementById('clearFilters');
    if (clearFiltersBtn) {
        clearFiltersBtn.addEventListener('click', function() {
            window.location.href = window.location.pathname;
        });
    }
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
    const originalValue = statusSelect.dataset.originalValue;
    
    // If no change, do nothing
    if (status === originalValue) {
        return;
    }
    
    // Get CSRF token
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
            
            // Update original value
            statusSelect.dataset.originalValue = status;
            
            // Show success toast
            showToast('Status Updated', data.message || 'Task status updated successfully');
        } else {
            // Show error toast and reset select
            showToast('Error', data.message || 'Failed to update task status');
            statusSelect.value = originalValue;
        }
    })
    .catch(error => {
        console.error('Error updating task status:', error);
        showToast('Error', 'Failed to update task status');
        statusSelect.value = originalValue;
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
    const batchUpdateBtn = document.querySelector('[data-bs-target="#batchUpdateModal"]');
    
    if (batchUpdateBtn) {
        if (selectedCount > 0) {
            batchUpdateBtn.innerHTML = `<i class="bi bi-pencil-square"></i> Batch Update (${selectedCount})`;
        } else {
            batchUpdateBtn.innerHTML = '<i class="bi bi-pencil-square"></i> Batch Update';
        }
    }
}

/**
 * Submit batch update for selected tasks
 */
function submitBatchUpdate() {
    const selectedTaskIds = Array.from(document.querySelectorAll('.task-checkbox:checked')).map(cb => cb.dataset.taskId);
    
    if (selectedTaskIds.length === 0) {
        document.getElementById('noTasksSelectedAlert').classList.remove('d-none');
        return;
    }
    
    document.getElementById('noTasksSelectedAlert').classList.add('d-none');
    
    // Get form data
    const form = document.getElementById('batchUpdateForm');
    const formData = new FormData(form);
    formData.append('task_ids', JSON.stringify(selectedTaskIds));
    
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    // Disable form inputs while submitting
    const formInputs = document.querySelectorAll('#batchUpdateForm select, #batchUpdateForm input');
    formInputs.forEach(input => {
        input.disabled = true;
    });
    
    // Disable submit button
    const submitBtn = document.getElementById('submitBatchUpdate');
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Updating...';
    
    // Convert FormData to URL-encoded string
    const urlEncodedData = new URLSearchParams();
    for (const pair of formData) {
        urlEncodedData.append(pair[0], pair[1]);
    }
    
    fetch('/games/tasks/batch_update/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': csrfToken
        },
        body: urlEncodedData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Show success toast
            showToast('Batch Update', data.message || `Updated ${selectedTaskIds.length} tasks successfully`);
            
            // Close modal
            const batchUpdateModal = bootstrap.Modal.getInstance(document.getElementById('batchUpdateModal'));
            batchUpdateModal.hide();
            
            // Reset form
            form.reset();
            
            // Reload page to reflect changes
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        } else {
            // Show error toast
            showToast('Error', data.message || 'Failed to update tasks');
            
            // Re-enable form inputs
            formInputs.forEach(input => {
                input.disabled = false;
            });
            
            // Reset submit button
            submitBtn.disabled = false;
            submitBtn.textContent = 'Update Tasks';
        }
    })
    .catch(error => {
        console.error('Error in batch update:', error);
        showToast('Error', 'Failed to update tasks');
        
        // Re-enable form inputs
        formInputs.forEach(input => {
            input.disabled = false;
        });
        
        // Reset submit button
        submitBtn.disabled = false;
        submitBtn.textContent = 'Update Tasks';
    });
}

/**
 * Show toast notification
 */
function showToast(title, message, type = 'info') {
    console.log('Showing toast:', title, message);
    const toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        console.warn('Toast container not found');
        return;
    }
    
    const toast = document.getElementById('taskToast');
    const toastTitle = document.getElementById('toastTitle');
    const toastMessage = document.getElementById('toastMessage');
    
    if (toast && toastTitle && toastMessage) {
        // Set toast content
        toastTitle.textContent = title;
        toastMessage.textContent = message;
        
        // Set toast type
        toast.className = 'toast';
        toast.classList.add(`bg-${type === 'success' ? 'success' : type === 'danger' ? 'danger' : 'light'}`);
        toast.classList.add(type === 'success' || type === 'danger' ? 'text-white' : 'text-dark');
        
        try {
            // Show toast
            const bsToast = new bootstrap.Toast(toast);
            bsToast.show();
        } catch (error) {
            console.error('Error showing toast:', error);
        }
    } else {
        console.warn('Toast elements not found:', {
            toast: !!toast,
            toastTitle: !!toastTitle,
            toastMessage: !!toastMessage
        });
    }
}
