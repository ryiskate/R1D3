/**
 * Global Task Manager JavaScript
 * Handles task filtering, status updates, batch operations, and notifications for the R1D3 Tasks dashboard
 */

/**
 * Normalize task type for backend compatibility
 */
function normalizeTaskType(taskType) {
    console.log('Normalizing task type:', taskType);
    
    // First check if it's already a normalized key
    const normalizedKeys = ['r1d3', 'game_development', 'education', 'social_media', 'arcade', 'theme_park', 'game'];
    if (normalizedKeys.includes(taskType.toLowerCase())) {
        console.log('Task type is already normalized:', taskType.toLowerCase());
        return taskType.toLowerCase();
    }
    
    // Map frontend class names to backend model keys
    const typeMap = {
        'R1D3Task': 'r1d3',
        'GameDevelopmentTask': 'game_development',
        'EducationTask': 'education',
        'SocialMediaTask': 'social_media',
        'ArcadeTask': 'arcade',
        'ThemeParkTask': 'theme_park',
        'GameTask': 'game'
    };
    
    // Try to match with case insensitivity
    for (const key in typeMap) {
        if (key.toLowerCase() === taskType.toLowerCase()) {
            console.log(`Matched ${taskType} to ${typeMap[key]}`);
            return typeMap[key];
        }
    }
    
    console.log('No match found, returning original:', taskType);
    return taskType;
}
document.addEventListener('DOMContentLoaded', function() {
    // Initialize DataTables with sorting
    if (document.getElementById('taskTable')) {
        const taskTable = $('#taskTable').DataTable({
            "order": [], // No initial sorting
            "columnDefs": [
                { "orderable": false, "targets": 0 }, // Checkbox column not sortable
                { "orderable": true, "targets": 6, // Due date column
                  "type": "date",
                  // Custom sorting for due dates that handles "No due date" text
                  "render": function(data, type, row) {
                      if (type === 'sort') {
                          // Extract date from the column content or return a far future date for "No due date"
                          const dateMatch = data.match(/([A-Z][a-z]{2}\s\d{1,2},\s\d{4})/);
                          if (dateMatch) {
                              return new Date(dateMatch[0]).getTime();
                          }
                          return new Date('9999-12-31').getTime(); // Far future date for "No due date"
                      }
                      return data;
                  }
                }
            ],
            "language": {
                "emptyTable": "No tasks found",
                "info": "Showing _START_ to _END_ of _TOTAL_ tasks",
                "search": "Search tasks:"
            },
            "pageLength": 25,
            "lengthMenu": [[10, 25, 50, -1], [10, 25, 50, "All"]]
        });
        
        // Re-initialize event listeners after DataTables initialization
        taskTable.on('draw', function() {
            // Re-attach status dropdown listeners
            attachStatusDropdownListeners();
            // Update checkbox listeners
            updateCheckboxListeners();
        });
    }
    
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

    // Initialize status dropdown handlers and checkbox listeners
    attachStatusDropdownListeners();
    updateCheckboxListeners();
    
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
function updateTaskStatus(element, taskId, taskType, status) {
    console.log(`Updating task ${taskId} (${taskType}) status to ${status}`);
    
    // Get CSRF token with fallback options
    let csrftoken = getCookie('csrftoken');
    
    // If CSRF token is still not found, try alternative methods
    if (!csrftoken) {
        // Try to get it from the meta tag
        const metaTag = document.querySelector('meta[name="csrf-token"]');
        if (metaTag) {
            csrftoken = metaTag.getAttribute('content');
            console.log('Using CSRF token from meta tag:', csrftoken);
        }
        
        // If still not found, check for Django's CSRF_COOKIE_NAME
        if (!csrftoken) {
            csrftoken = getCookie('csrf');
            console.log('Using csrf cookie:', csrftoken);
        }
    }
    
    console.log(`CSRF token: ${csrftoken ? 'Found' : 'Not found'}`);
    
    // Show loading state
    const originalBadgeHtml = element.innerHTML;
    element.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Updating...';
    
    // Normalize task type for backend compatibility
    const normalizedTaskType = normalizeTaskType(taskType);
    console.log(`Normalized task type: ${normalizedTaskType}`);
    
    // Create form data for the request
    const formData = new FormData();
    formData.append('task_id', taskId);
    formData.append('task_type', normalizedTaskType);
    formData.append('status', status);
    
    // Add CSRF token to form data as a fallback
    if (csrftoken) {
        formData.append('csrfmiddlewaretoken', csrftoken);
    }
    
    // Make AJAX call with XMLHttpRequest for better compatibility
    const xhr = new XMLHttpRequest();
    xhr.open('POST', '/R1D3-tasks/update-status/');
    xhr.setRequestHeader('X-CSRFToken', csrftoken);
    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    
    xhr.onload = function() {
        console.log('XHR response received - Status:', xhr.status);
        console.log('XHR response text:', xhr.responseText);
        
        if (xhr.status >= 200 && xhr.status < 300) {
            try {
                const response = JSON.parse(xhr.responseText);
                console.log('Parsed response:', response);
                
                // Update UI
                const statusBadge = element.closest('.status-dropdown').querySelector('.status-badge');
                const taskRow = element.closest('tr.task-row');
                
                if (statusBadge && taskRow) {
                    // Update badge color
                    statusBadge.style.backgroundColor = getStatusColor(status);
                    
                    // Update badge text
                    statusBadge.textContent = getStatusDisplayText(status);
                    
                    // Update row data attribute
                    taskRow.dataset.status = status;
                    
                    // Show success message
                    showToast('Success', 'Task status updated successfully', 'success');
                    
                    // Log the successful update
                    console.log(`Task ${taskId} status updated to ${status} successfully`);
                } else {
                    console.error('Could not find status badge or task row');
                    showToast('Warning', 'Status updated but UI could not be refreshed', 'warning');
                }
            } catch (e) {
                console.error('Error parsing response:', e);
                element.innerHTML = originalBadgeHtml;
                showToast('Error', 'Could not parse server response', 'danger');
            }
        } else {
            console.error('Error response:', xhr.status, xhr.responseText);
            element.innerHTML = originalBadgeHtml;
            
            // Try to parse error message from response
            try {
                const errorResponse = JSON.parse(xhr.responseText);
                showToast('Error', errorResponse.error || 'Failed to update task status', 'danger');
            } catch (e) {
                showToast('Error', 'Failed to update task status', 'danger');
            }
        }
    };
    
    xhr.onerror = function() {
        console.error('Network error occurred');
        element.innerHTML = originalBadgeHtml;
        showToast('Error', 'Network error occurred', 'danger');
    };
    
    console.log('Sending XHR request...');
    xhr.send(urlEncodedData);
    
    // For debugging, also try a simple fetch to test the endpoint with form data
    fetch('/R1D3-tasks/update-status/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': csrftoken
        },
        body: formDataString
    })
    .then(response => {
        if (!response.ok) {
            return response.text().then(text => {
                console.error('Server response:', text);
                throw new Error(`Network response was not ok: ${response.status} ${response.statusText}`);
            });
        }
        return response.json();
    })
    .then(data => {
        // Update the status badge in the UI
        const statusBadge = element.closest('.status-dropdown').querySelector('.status-badge');
        const newBadgeColor = getStatusColor(status);
        statusBadge.style.backgroundColor = newBadgeColor;
        statusBadge.textContent = getStatusDisplayName(status);
        
        // Update the task row data attribute
        const taskRow = element.closest('tr');
        taskRow.dataset.status = status;
        
        // Show success message
        showToast('Status Updated', `Task #${taskId} status changed to ${getStatusDisplayName(status)}`, 'success');
    })
    .catch(error => {
        console.error('Error updating task status:', error);
        showToast('Error', 'Failed to update task status. Please try again.', 'danger');
    })
    .finally(() => {
        // Restore original button content
        element.innerHTML = originalBadgeHtml;
    });
}

/**
 * Get status display name
 */
function getStatusDisplayName(status) {
    const statusMap = {
        'to_do': 'To Do',
        'in_progress': 'In Progress',
        'in_review': 'In Review',
        'done': 'Done',
        'backlog': 'Backlog',
        'blocked': 'Blocked'
    };
    return statusMap[status] || status.charAt(0).toUpperCase() + status.slice(1);
}

/**
 * Get color for status
 */
function getStatusColor(status) {
    const colors = {
        'to_do': '#0d6efd',      // blue
        'todo': '#0d6efd',       // blue
        'in_progress': '#ffc107', // yellow
        'in_review': '#6f42c1',   // purple
        'done': '#198754',        // green
        'backlog': '#6c757d',     // gray
        'blocked': '#dc3545'      // red
    };
    
    return colors[status] || '#6c757d'; // default to gray
}

/**
 * Get display text for status
 */
function getStatusDisplayText(status) {
    const displayTexts = {
        'to_do': 'To Do',
        'todo': 'To Do',
        'in_progress': 'In Progress',
        'in_review': 'In Review',
        'done': 'Done',
        'backlog': 'Backlog',
        'blocked': 'Blocked'
    };
    
    return displayTexts[status] || status.charAt(0).toUpperCase() + status.slice(1).replace('_', ' ');
}

/**
 * Get CSRF token from cookies
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        console.log('All cookies:', cookies);
        
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            console.log(`Checking cookie: ${cookie}`);
            
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                console.log(`Found ${name} cookie:`, cookieValue);
                break;
            }
        }
    } else {
        console.warn('No cookies found in document');
    }
    
    if (!cookieValue) {
        console.error(`${name} cookie not found`);
        
        // Fallback: try to get from the csrftoken input if it exists
        const csrfInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
        if (csrfInput && name === 'csrftoken') {
            cookieValue = csrfInput.value;
            console.log('Using CSRF token from input field:', cookieValue);
        }
    }
    
    return cookieValue;
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
 * Normalize task type for backend compatibility
 */
function normalizeTaskType(taskType) {
    // Map class names to task types expected by the backend
    const taskTypeMap = {
        'R1D3Task': 'r1d3',
        'GameDevelopmentTask': 'game_development',
        'EducationTask': 'education',
        'SocialMediaTask': 'social_media',
        'ArcadeTask': 'arcade',
        'ThemeParkTask': 'theme_park',
        'GameTask': 'game'
    };
    
    // Return the mapped value or the original if not found
    return taskTypeMap[taskType] || taskType;
}

/**
 * Attach event listeners to status dropdown items
 */
function attachStatusDropdownListeners() {
    const statusOptions = document.querySelectorAll('.status-option');
    statusOptions.forEach(option => {
        option.removeEventListener('click', handleStatusOptionClick);
        option.addEventListener('click', handleStatusOptionClick);
    });
    // Status dropdown handling - initial attachment
    attachStatusDropdownListeners();
}

/**
 * Handle status option click event
 */
function handleStatusOptionClick(event) {
    event.preventDefault();
    const statusOption = event.currentTarget;
    const status = statusOption.getAttribute('data-status');
    const dropdownMenu = statusOption.closest('.dropdown-menu');
    const taskId = dropdownMenu.getAttribute('data-task-id');
    const taskType = dropdownMenu.getAttribute('data-task-type');
    
    updateTaskStatus(statusOption, taskId, taskType, status);
}

/**
 * Update checkbox listeners after DataTables redraws
 */
function updateCheckboxListeners() {
    const selectAllCheckbox = document.getElementById('selectAllTasks');
    const taskCheckboxes = document.querySelectorAll('.task-checkbox');
    
    // Re-attach checkbox event listeners
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function() {
            taskCheckboxes.forEach(checkbox => {
                checkbox.checked = selectAllCheckbox.checked;
            });
            updateSelectedCount();
        });
    }
    
    taskCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            updateSelectedCount();
            
            // Update select all checkbox state
            if (selectAllCheckbox) {
                const allChecked = Array.from(taskCheckboxes).every(cb => cb.checked);
                const someChecked = Array.from(taskCheckboxes).some(cb => cb.checked);
                
                selectAllCheckbox.checked = allChecked;
                selectAllCheckbox.indeterminate = someChecked && !allChecked;
            }
        });
    });
}

/**
 * Show toast notification
 */
function showToast(title, message, type = 'info') {
    const toastContainer = document.getElementById('toastContainer');
    if (!toastContainer) return;
    
    const toastId = 'toast-' + Date.now();
    const bgClass = type === 'success' ? 'bg-success' : 
                   type === 'warning' ? 'bg-warning' :
                   type === 'error' ? 'bg-danger' : 'bg-info';
    
    const toastHtml = `
        <div id="${toastId}" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="toast-header ${bgClass} text-white">
                <strong class="me-auto">${title}</strong>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        </div>
    `;
    
    toastContainer.insertAdjacentHTML('beforeend', toastHtml);
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement, { delay: 5000 });
    toast.show();
    
    // Remove toast from DOM after it's hidden
    toastElement.addEventListener('hidden.bs.toast', function() {
        toastElement.remove();
    });
}
