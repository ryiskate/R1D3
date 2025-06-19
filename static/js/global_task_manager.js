/**
 * Global Task Manager JavaScript
 * Handles task filtering, status updates, batch operations, and notifications for the R1D3 Tasks dashboard
 */
document.addEventListener('DOMContentLoaded', function() {
    // Initialize elements
    const selectAllCheckbox = document.getElementById('selectAllTasks');
    const taskCheckboxes = document.querySelectorAll('.task-checkbox');
    const selectedTasksCount = document.getElementById('batchSelectedCount');
    const batchUpdateSubmit = document.getElementById('batchUpdateSubmit');
    
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
    
    // Function to update selected count
    function updateSelectedCount() {
        const selectedCount = document.querySelectorAll('.task-checkbox:checked').length;
        if (selectedTasksCount) {
            selectedTasksCount.textContent = selectedCount;
        }
        if (batchUpdateSubmit) {
            batchUpdateSubmit.disabled = selectedCount === 0;
        }
    }
    
    // Select all checkbox
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function() {
            taskCheckboxes.forEach(checkbox => {
                checkbox.checked = selectAllCheckbox.checked;
            });
            updateSelectedCount();
        });
    }
    
    // Individual task checkboxes
    taskCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            updateSelectedCount();
            
            // Update select all checkbox state
            if (!this.checked) {
                selectAllCheckbox.checked = false;
            } else {
                // Check if all checkboxes are checked
                const allChecked = Array.from(taskCheckboxes).every(c => c.checked);
                selectAllCheckbox.checked = allChecked;
            }
        });
    });
    
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
    
    // Initialize on page load
    updateSelectedCount();
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
    const status = form.querySelector('select').value;
    
    // Here you would typically make an AJAX call to update the task status
    console.log('Updating task', taskId, 'to status', status);
    
    // Show success message
    showToast('Status Updated', `Task #${taskId} status changed to ${status}`, 'success');
}

/**
 * Submit batch update for selected tasks
 */
function submitBatchUpdate() {
    const selectedTaskIds = Array.from(document.querySelectorAll('.task-checkbox:checked'))
        .map(checkbox => checkbox.dataset.taskId);
    const status = document.getElementById('batchStatus').value;
    
    // Here you would typically make an AJAX call to update the tasks
    console.log('Updating tasks', selectedTaskIds, 'to status', status);
    
    // Show success message
    showToast('Batch Update', `Successfully updated ${selectedTaskIds.length} tasks.`, 'success');
    
    // Close the modal
    const batchUpdateModal = document.getElementById('batchUpdateModal');
    const bsModal = bootstrap.Modal.getInstance(batchUpdateModal);
    bsModal.hide();
    
    // Reset form
    const selectAllCheckbox = document.getElementById('selectAllTasks');
    if (selectAllCheckbox) {
        selectAllCheckbox.checked = false;
    }
    
    document.querySelectorAll('.task-checkbox').forEach(checkbox => {
        checkbox.checked = false;
    });
    
    // Update selected count
    const selectedTasksCount = document.getElementById('batchSelectedCount');
    const batchUpdateSubmit = document.getElementById('batchUpdateSubmit');
    if (selectedTasksCount) {
        selectedTasksCount.textContent = '0';
    }
    if (batchUpdateSubmit) {
        batchUpdateSubmit.disabled = true;
    }
}

/**
 * Show toast notification
 */
function showToast(title, message, type = 'info') {
    const toastContainer = document.getElementById('toastContainer');
    if (!toastContainer) return;
    
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type}`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                <strong>${title}</strong>: ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;
    toastContainer.appendChild(toast);
    
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    // Remove toast after it's hidden
    toast.addEventListener('hidden.bs.toast', function() {
        toast.remove();
    });
}
