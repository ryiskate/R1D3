/**
 * Simple Status Updater Script
 * This script focuses only on handling status updates for tasks
 */

console.log('%c STATUS UPDATER SCRIPT LOADED', 'background: #3498db; color: white; padding: 10px; font-size: 16px; font-weight: bold;');

// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('%c Status Updater: DOM Ready', 'background: #2ecc71; color: white; padding: 5px;');
    
    // Find all status dropdown items
    const statusItems = document.querySelectorAll('.status-option');
    console.log(`Found ${statusItems.length} status dropdown items with class 'status-option'`);
    
    if (statusItems.length === 0) {
        // Try alternative selector
        const altStatusItems = document.querySelectorAll('.dropdown-item[data-status]');
        console.log(`Found ${altStatusItems.length} status dropdown items with attribute 'data-status'`);
        
        if (altStatusItems.length > 0) {
            attachListeners(altStatusItems);
            return;
        }
        
        // If still no items found, log the HTML structure
        console.error('No status dropdown items found with either selector');
        document.querySelectorAll('.status-dropdown').forEach((dropdown, i) => {
            console.log(`Status dropdown ${i} HTML:`, dropdown.innerHTML);
        });
    } else {
        attachListeners(statusItems);
    }
});

/**
 * Attach click event listeners to status dropdown items
 */
function attachListeners(items) {
    console.log(`Attaching listeners to ${items.length} status items`);
    
    items.forEach((item, index) => {
        // Clone the node to remove any existing event listeners
        const newItem = item.cloneNode(true);
        item.parentNode.replaceChild(newItem, item);
        
        console.log(`Attaching listener to status item ${index}: ${newItem.textContent.trim()}`);
        
        newItem.addEventListener('click', function(event) {
            event.preventDefault();
            event.stopPropagation();
            
            console.log('%c STATUS ITEM CLICKED!', 'background: #e74c3c; color: white; padding: 10px; font-size: 16px; font-weight: bold;');
            console.log('Clicked item:', this.textContent.trim());
            
            // Get task information from the dropdown
            const dropdown = this.closest('.dropdown');
            if (!dropdown) {
                console.error('Could not find parent dropdown');
                return;
            }
            
            const taskId = dropdown.dataset.taskId;
            const taskType = dropdown.dataset.taskType;
            const status = this.dataset.status;
            
            console.log('Task ID:', taskId);
            console.log('Task Type:', taskType);
            console.log('New Status:', status);
            
            // Update the status via AJAX
            updateStatus(this, taskId, taskType, status);
        });
    });
}

/**
 * Update task status via AJAX
 */
function updateStatus(element, taskId, taskType, status) {
    console.log('%c UPDATING STATUS...', 'background: #f39c12; color: white; padding: 5px;');
    
    // Get CSRF token
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || getCookie('csrftoken');
    console.log('CSRF Token:', csrftoken ? 'Found' : 'Not found');
    
    if (!csrftoken) {
        console.error('CSRF token not found');
        showToast('Error', 'Security token not found. Please refresh the page and try again.', 'error');
        return;
    }
    
    // Find the status badge
    const dropdown = element.closest('.dropdown');
    const statusBadge = dropdown.querySelector('.status-badge');
    
    if (!statusBadge) {
        console.error('Could not find status badge');
        return;
    }
    
    // Show loading state
    const originalBadgeHtml = statusBadge.innerHTML;
    const originalBadgeColor = statusBadge.style.backgroundColor;
    statusBadge.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>';
    
    // Normalize task type
    const normalizedTaskType = normalizeTaskType(taskType);
    
    // Create form data
    const formData = new FormData();
    formData.append('task_id', taskId);
    formData.append('task_type', normalizedTaskType);
    formData.append('status', status);
    formData.append('csrfmiddlewaretoken', csrftoken);
    
    // Store these for error handling
    const requestData = {
        taskId,
        taskType,
        normalizedTaskType,
        status
    };
    
    console.log('Sending request to:', '/R1D3-tasks/update-status/');
    
    // Log the exact payload being sent
    console.log('%c FORM DATA BEING SENT:', 'background: #3498db; color: white; padding: 5px;');
    for (let pair of formData.entries()) {
        console.log(pair[0] + ': ' + pair[1]);
    }
    
    // Send AJAX request
    fetch('/R1D3-tasks/update-status/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: formData,
        credentials: 'same-origin'
    })
    .then(response => {
        console.log('%c SERVER RESPONSE:', 'background: #f39c12; color: white; padding: 5px;');
        console.log('Status:', response.status);
        console.log('Status Text:', response.statusText);
        console.log('Headers:', response.headers);
        
        // Clone the response so we can both read the text and parse as JSON if possible
        const clonedResponse = response.clone();
        
        // First try to get the raw text
        clonedResponse.text().then(text => {
            console.log('Response Text:', text);
        }).catch(err => {
            console.error('Error reading response text:', err);
        });
        
        if (!response.ok) {
            throw new Error(`Server returned ${response.status}: ${response.statusText}`);
        }
        
        return response.json();
    })
    .then(data => {
        console.log('%c STATUS UPDATED SUCCESSFULLY!', 'background: #2ecc71; color: white; padding: 10px; font-size: 16px; font-weight: bold;');
        console.log('Response:', data);
        
        // Update the status badge
        statusBadge.textContent = getStatusDisplayText(status);
        statusBadge.style.backgroundColor = getStatusColor(status);
        
        // Update row data attribute
        const taskRow = dropdown.closest('tr');
        if (taskRow) {
            taskRow.setAttribute('data-status', status);
        }
        
        // Show success toast
        showToast('Success', `Task status changed to ${getStatusDisplayText(status)}`, 'success');
    })
    .catch(error => {
        console.error('%c STATUS UPDATE FAILED!', 'background: #e74c3c; color: white; padding: 10px; font-size: 16px; font-weight: bold;');
        console.error('Error:', error);
        
        // Try to get more information about the error
        console.log('%c DEBUGGING SERVER ERROR', 'background: #8e44ad; color: white; padding: 5px;');
        console.log('Task ID:', requestData.taskId);
        console.log('Task Type:', requestData.taskType);
        console.log('Normalized Task Type:', requestData.normalizedTaskType);
        console.log('Status:', requestData.status);
        
        // Check if the task type is one of the expected values in the server
        const validTaskTypes = ['r1d3task', 'gametask', 'gamedevelopmenttask', 'educationtask', 'socialmediatask', 'arcadetask', 'themeparktask'];
        console.log('Is task type valid?', validTaskTypes.includes(requestData.normalizedTaskType.toLowerCase()));
        
        // Restore original badge
        statusBadge.innerHTML = originalBadgeHtml;
        statusBadge.style.backgroundColor = originalBadgeColor;
        
        // Show error toast with more details
        showToast('Error', `Failed to update status: ${error.message}. Check console for details.`, 'error');
    });
}

/**
 * Helper function to get a cookie by name
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/**
 * Normalize task type for backend compatibility
 */
function normalizeTaskType(taskType) {
    if (!taskType) return '';
    
    // Log the original task type
    console.log('Original task type:', taskType);
    
    // Convert to lowercase for consistent matching
    const lowerType = taskType.toLowerCase();
    
    // Map of task types from frontend to backend format
    // This matches EXACTLY what the server expects in views.py:update_task_status
    const taskTypeMap = {
        'gametask': 'gametask',
        'r1d3task': 'r1d3task',
        'socialmediatask': 'socialmediatask',
        'educationtask': 'educationtask',
        'arcadetask': 'arcadetask',
        'themeparktask': 'themeparktask',
        'gamedevelopmenttask': 'gamedevelopmenttask',
        // Add snake_case versions too
        'game_task': 'gametask',
        'r1d3_task': 'r1d3task',
        'social_media_task': 'socialmediatask',
        'education_task': 'educationtask',
        'arcade_task': 'arcadetask',
        'theme_park_task': 'themeparktask',
        'game_development_task': 'gamedevelopmenttask',
        // Add class names without 'task' suffix
        'game': 'gametask',
        'r1d3': 'r1d3task',
        'socialmedia': 'socialmediatask',
        'education': 'educationtask',
        'arcade': 'arcadetask',
        'themepark': 'themeparktask',
        'gamedevelopment': 'gamedevelopmenttask'
    };
    
    // Return the mapped value if it exists, otherwise return the original
    const normalizedType = taskTypeMap[lowerType] || taskType;
    console.log('Normalized task type:', normalizedType);
    
    return normalizedType;
}

/**
 * Get status display text based on status code
 */
function getStatusDisplayText(status) {
    switch (status) {
        case 'to_do': return 'To Do';
        case 'in_progress': return 'In Progress';
        case 'review': return 'Review';
        case 'done': return 'Done';
        case 'blocked': return 'Blocked';
        default: return status.charAt(0).toUpperCase() + status.slice(1).replace('_', ' ');
    }
}

/**
 * Get status color based on status code
 */
function getStatusColor(status) {
    switch (status) {
        case 'to_do': return '#0d6efd'; // Blue
        case 'in_progress': return '#ffc107'; // Yellow
        case 'review': return '#6f42c1'; // Purple
        case 'done': return '#198754'; // Green
        case 'blocked': return '#dc3545'; // Red
        default: return '#6c757d'; // Gray
    }
}

/**
 * Show a toast notification
 */
function showToast(title, message, type = 'info') {
    // Create toast container if it doesn't exist
    let toastContainer = document.getElementById('toastContainer');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toastContainer';
        toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
        toastContainer.style.zIndex = '1050';
        document.body.appendChild(toastContainer);
    }
    
    // Set color based on type
    let bgColor = 'bg-info';
    if (type === 'success') bgColor = 'bg-success';
    if (type === 'error' || type === 'danger') bgColor = 'bg-danger';
    if (type === 'warning') bgColor = 'bg-warning';
    
    // Create a unique ID for the toast
    const toastId = 'toast-' + Date.now();
    
    // Create toast HTML
    const toastHtml = `
        <div id="${toastId}" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="toast-header ${bgColor} text-white">
                <strong class="me-auto">${title}</strong>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        </div>
    `;
    
    // Add toast to container
    toastContainer.insertAdjacentHTML('beforeend', toastHtml);
    
    // Initialize and show the toast
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement, { autohide: true, delay: 5000 });
    toast.show();
    
    console.log(`Toast shown: ${title} - ${message}`);
}
