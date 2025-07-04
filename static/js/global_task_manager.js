/**
 * Global Task Manager JavaScript
 * Handles task filtering, status updates, batch operations, and notifications for the R1D3 Tasks dashboard
 * Version: 2.0 - Fixed sorting and status updates
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

/**
 * Helper function to get a cookie by name
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/**
 * Show a toast notification
 * @param {string} type - The type of toast (success, danger, warning, info)
 * @param {string} title - The toast title
 * @param {string} message - The toast message
 */
function showToast(type, title, message) {
    console.log(`Showing ${type} toast: ${title} - ${message}`);
    
    // Create toast container if it doesn't exist
    let toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(toastContainer);
    }
    
    // Create a unique ID for this toast
    const toastId = 'toast-' + Date.now();
    
    // Set the appropriate background color based on type
    let bgClass = 'bg-primary';
    switch (type) {
        case 'success':
            bgClass = 'bg-success';
            break;
        case 'danger':
            bgClass = 'bg-danger';
            break;
        case 'warning':
            bgClass = 'bg-warning';
            break;
        case 'info':
            bgClass = 'bg-info';
            break;
    }
    
    // Create the toast HTML
    const toastHtml = `
        <div id="${toastId}" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="toast-header ${bgClass} text-white">
                <strong class="me-auto">${title}</strong>
                <small>Just now</small>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        </div>
    `;
    
    // Add the toast to the container
    toastContainer.insertAdjacentHTML('beforeend', toastHtml);
    
    // Initialize and show the toast
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement, {
        autohide: true,
        delay: 5000
    });
    toast.show();
    
    // Remove the toast element after it's hidden
    toastElement.addEventListener('hidden.bs.toast', function() {
        toastElement.remove();
    });
}

// Initialize everything when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('%c R1D3 Task Manager Initializing...', 'background: #3498db; color: white; padding: 5px; border-radius: 3px; font-weight: bold;');
    
    // Debug information about the environment
    console.log('jQuery version:', typeof $ !== 'undefined' ? $.fn.jquery : 'Not loaded');
    console.log('DataTables version:', typeof $.fn.dataTable !== 'undefined' ? $.fn.dataTable.version : 'Not loaded');
    console.log('Bootstrap version:', typeof bootstrap !== 'undefined' ? bootstrap.Tooltip.VERSION : 'Not loaded');
    
    // Check if task table exists
    const taskTable = document.getElementById('taskTable');
    if (!taskTable) {
        console.error('Task table not found in DOM!');
    } else {
        console.log('Task table found:', taskTable);
        console.log('Task table columns:', taskTable.querySelectorAll('th').length);
        console.log('Due Date column:', taskTable.querySelector('th:nth-child(7)').textContent);
    }
    
    // Initialize DataTables with sorting
    if (taskTable && typeof $ !== 'undefined') {
        console.log('%c Initializing DataTables...', 'background: #2ecc71; color: white; padding: 3px; border-radius: 3px;');
        
        // Register custom DataTables sorting for dates
        if ($.fn.dataTable) {
            console.log('Registering custom DataTables date sorting');
            
            // Add a custom date detection type that can handle multiple formats
            $.fn.dataTable.ext.type.detect.unshift(function(data) {
                if (!data) return null;
                data = String(data); // Ensure data is a string
                
                console.log('Detecting data type for:', data);
                
                // If it's our special 'No due date' text
                if (data.trim() === 'No due date') {
                    console.log('Detected "No due date" text');
                    return 'date-detect';
                }
                
                // Try to parse the date with moment.js
                if (typeof moment !== 'undefined' && 
                    moment(data, ['YYYY-MM-DD', 'MM/DD/YYYY', 'DD/MM/YYYY', 'MMM D, YYYY'], true).isValid()) {
                    console.log('Detected valid date:', data);
                    return 'date-detect';
                }
                
                return null;
            });
            
            // Define how to pre-process the data for ordering
            $.fn.dataTable.ext.type.order['date-detect-pre'] = function(data) {
                if (!data) return 0;
                data = String(data); // Ensure data is a string
                
                console.log('Ordering date:', data);
                
                // Handle 'No due date' as a far future date (so it sorts to the end)
                if (data.trim() === 'No due date') {
                    console.log('Ordering "No due date" as far future');
                    return 9999999999999; // A very large timestamp
                }
                
                // Try to parse the date with moment.js
                if (typeof moment !== 'undefined') {
                    const parsed = moment(data, ['YYYY-MM-DD', 'MM/DD/YYYY', 'DD/MM/YYYY', 'MMM D, YYYY']);
                    if (parsed.isValid()) {
                        console.log('Parsed date for ordering:', parsed.valueOf());
                        return parsed.valueOf(); // Return timestamp for sorting
                    }
                }
                
                // If all parsing attempts fail, return a large number
                // so these values appear at the end when sorting
                console.log('Failed to parse date:', data);
                return 9999999999999;
            };
            
            console.log('Custom date sorting registered');
        }
        
        // Initialize DataTables with explicit configuration
        console.log('DataTable columns:', $('#taskTable th').length);
        $('#taskTable th').each(function(index) {
            console.log(`Column ${index}: ${$(this).text().trim()}`);
        });
        
        const taskTable = $('#taskTable').DataTable({
            // Debug DataTables initialization
            "initComplete": function(settings, json) {
                console.log('%c DataTables initialization complete!', 'background: #2ecc71; color: white; padding: 5px; border-radius: 3px;');
                console.log('DataTables settings:', settings);
                console.log('Columns:', settings.aoColumns);
            },
            // Initial sorting by due date ascending
            "order": [[6, 'asc']], 
            // Show processing indicator
            "processing": true,
            // Client-side processing (not server-side)
            "serverSide": false,
            // Column definitions
            "columnDefs": [
                // Checkbox column not sortable
                { "orderable": false, "targets": 0 },
                // Actions column not sortable
                { "orderable": false, "targets": 7 },
                // Title column (Task)
                { 
                    "orderable": true, 
                    "targets": 1,
                    "title": "Task"
                },
                // Due date column with custom sorting
                { 
                    "orderable": true, 
                    "targets": 6,
                    "type": 'date-detect'
                },
                // Make all other columns explicitly sortable
                { "orderable": true, "targets": [2, 3, 4, 5] }
            ],
            // Disable DataTables' auto-width calculation
            "autoWidth": false,
            // Enable sorting buttons
            "ordering": true,
            // Make sure the table header is clickable
            "headerCallback": function(thead, data, start, end, display) {
                $(thead).find('th').addClass('sorting_enabled').css('cursor', 'pointer');
            },
            "language": {
                "emptyTable": "No tasks found",
                "info": "Showing _START_ to _END_ of _TOTAL_ tasks",
                "search": "Search tasks:"
            },
            "pageLength": 25,
            "lengthMenu": [[10, 25, 50, -1], [10, 25, 50, "All"]],
            "drawCallback": function(settings) {
                // Re-attach event listeners
                setTimeout(function() {
                    console.log('Attaching event listeners after DataTables initialization');
                    attachStatusDropdownListeners();
                    
                    // Re-attach event listeners when DataTables redraws the table
                    $('#taskTable').on('draw.dt', function() {
                        console.log('DataTable redrawn, re-attaching event listeners');
                        attachStatusDropdownListeners();
                        updateCheckboxListeners();
                    });
                }, 500); // Small delay to ensure DataTables is fully initialized
            }
        });
        
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
    }
    
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

    // After DataTables is initialized, attach event listeners
    setTimeout(function() {
        console.log('Attaching event listeners after DataTables initialization');
        attachStatusDropdownListeners();
        updateCheckboxListeners();
    }, 500); // Small delay to ensure DataTables is fully initialized
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
    console.log('%c Updating task status...', 'background: #f39c12; color: white; padding: 5px; border-radius: 3px; font-weight: bold;');
    console.log('Task ID:', taskId);
    console.log('Task Type:', taskType);
    console.log('New Status:', status);
    console.log('Element:', element);
    
    if (!taskId) {
        console.error('Task ID is missing!');
        showToast('error', 'Error', 'Task ID is missing. Cannot update status.');
        return;
    }
    
    if (!taskType) {
        console.error('Task Type is missing!');
        showToast('error', 'Error', 'Task type is missing. Cannot update status.');
        return;
    }
    
    // Get CSRF token
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || getCookie('csrftoken');
    console.log('CSRF Token:', csrftoken ? 'Found' : 'Not found');
    
    if (!csrftoken) {
        console.error('CSRF token not found');
        showToast('error', 'Error', 'Security token not found. Please refresh the page and try again.');
        return;
    }
    
    // Find the status badge and row
    let statusBadge = null;
    let taskRow = null;
    
    console.log('Finding status badge and task row...');
    
    // Try to find the status badge directly from the element's hierarchy
    if (element) {
        console.log('Searching from clicked element:', element);
        const dropdown = element.closest('.dropdown');
        if (dropdown) {
            console.log('Found dropdown parent:', dropdown);
            statusBadge = dropdown.querySelector('.status-badge');
            taskRow = dropdown.closest('tr');
            console.log('Found from element hierarchy - Badge:', statusBadge, 'Row:', taskRow);
        } else {
            console.log('No dropdown parent found from element');
        }
    } else {
        console.log('No element provided to search from');
    }
    
    // If not found, try to find by task ID
    if (!statusBadge || !taskRow) {
        console.log('Searching by task ID:', taskId);
        const dropdown = findStatusDropdownByTaskId(taskId);
        if (dropdown) {
            console.log('Found dropdown by task ID:', dropdown);
            statusBadge = dropdown.querySelector('.status-badge');
            taskRow = dropdown.closest('tr');
            console.log('Found by task ID - Badge:', statusBadge, 'Row:', taskRow);
        } else {
            console.log('No dropdown found by task ID');
        }
    }
    
    // If still not found, try to find the row directly
    if (!taskRow || !statusBadge) {
        console.log('Searching for row directly by task ID');
        taskRow = document.querySelector(`tr[data-task-id="${taskId}"]`);
        if (taskRow) {
            console.log('Found task row directly:', taskRow);
            const dropdown = taskRow.querySelector('.status-dropdown');
            if (dropdown) {
                console.log('Found dropdown in row:', dropdown);
                statusBadge = dropdown.querySelector('.status-badge');
                console.log('Found status badge in dropdown:', statusBadge);
            } else {
                console.log('No dropdown found in row');
            }
        } else {
            console.log('No task row found directly');
        }
    }
    
    if (!statusBadge) {
        console.error('Could not find status badge element');
        showToast('error', 'Error', 'Could not find the status indicator. Please refresh the page and try again.');
        return;
    }
    
    // Show loading state
    const originalBadgeHtml = statusBadge.innerHTML;
    const originalBadgeColor = statusBadge.style.backgroundColor;
    statusBadge.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>';
    
    // Normalize task type for backend compatibility
    const normalizedTaskType = normalizeTaskType(taskType);
    
    // Create form data for the request
    const formData = new FormData();
    formData.append('task_id', taskId);
    formData.append('task_type', normalizedTaskType);
    formData.append('status', status);
    formData.append('csrfmiddlewaretoken', csrftoken);
    
    console.log('Sending AJAX request with data:');
    console.log('- Task ID:', taskId);
    console.log('- Task Type (normalized):', normalizedTaskType);
    console.log('- Status:', status);
    console.log('- CSRF Token:', csrftoken ? 'Present' : 'Missing');
    console.log('- URL:', '/R1D3-tasks/update-status/');
    
    // Debug the URL we're posting to
    console.log('%c POSTING TO URL:', 'background: #e74c3c; color: white; padding: 5px;', '/R1D3-tasks/update-status/');
    
    // Use fetch API with proper headers
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
        if (!response.ok) {
            throw new Error(`Server returned ${response.status}: ${response.statusText}`);
        }
        return response.json();
    })
    .then(data => {
        console.log('%c STATUS CHANGED SUCCESSFULLY!', 'background: #2ecc71; color: white; padding: 10px; font-size: 16px; font-weight: bold;');
        console.log('Response data:', data);
        
        // Update the status badge
        statusBadge.textContent = getStatusDisplayText(status);
        statusBadge.style.backgroundColor = getStatusColor(status);
        console.log('Updated status badge text to:', getStatusDisplayText(status));
        console.log('Updated status badge color to:', getStatusColor(status));
        
        // Update row data attribute
        if (taskRow) {
            taskRow.setAttribute('data-status', status);
            console.log('Updated row data-status attribute to:', status);
        }
        
        // Show success toast notification
        showToast('success', 'Task Status Updated', `Task status changed to ${getStatusDisplayText(status)}`);
        console.log('Displayed success toast notification');
        
        // Add a visible console message that will be easy to spot
        console.log('%c ✅ TASK STATUS UPDATED TO: ' + status.toUpperCase() + ' ✅', 'background: #27ae60; color: white; padding: 15px; font-size: 20px; font-weight: bold; border-radius: 5px;');
    })
    .catch(error => {
        console.error('%c STATUS UPDATE FAILED!', 'background: #e74c3c; color: white; padding: 10px; font-size: 16px; font-weight: bold;');
        console.error('Error details:', error);
        
        // Try to get more information about the error
        if (error.response) {
            console.error('Response status:', error.response.status);
            console.error('Response data:', error.response.data);
        }
        
        // Restore original badge
        statusBadge.innerHTML = originalBadgeHtml;
        statusBadge.style.backgroundColor = originalBadgeColor;
        console.log('Restored original badge state');
        
        // Show error toast notification
        showToast('danger', 'Status Update Failed', `Error: ${error.message}`);
        console.log('Displayed error toast notification');
        
        // Add a visible console message that will be easy to spot
        console.log('%c ❌ STATUS UPDATE FAILED ❌', 'background: #c0392b; color: white; padding: 15px; font-size: 20px; font-weight: bold; border-radius: 5px;');
    });
}

/**
 * Show toast notification
 */
function showToast(title, message, type = 'info') {
    // Check if we have a toast container, if not create one
    let toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(toastContainer);
    }
    
    // Create a unique ID for the toast
    const toastId = 'toast-' + Date.now();
    
    // Create the toast HTML
    const toastHtml = `
        <div id="${toastId}" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="toast-header bg-${type} text-white">
                <strong class="me-auto">${title}</strong>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        </div>
    `;
    
    // Add the toast to the container
    toastContainer.insertAdjacentHTML('beforeend', toastHtml);
    
    // Initialize the toast
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement, {
        autohide: true,
        delay: 5000
    });
    
    // Show the toast
    toast.show();
    
    // Remove the toast from the DOM after it's hidden
    toastElement.addEventListener('hidden.bs.toast', function() {
        toastElement.remove();
    });
}

/**
 * Find status dropdown by task ID
 */
function findStatusDropdownByTaskId(taskId) {
    const dropdowns = document.querySelectorAll('.status-dropdown[data-task-id]');
    for (const dropdown of dropdowns) {
        if (dropdown.dataset.taskId === taskId) {
            return dropdown;
        }
    }
    return null;
}

/**
 * Get status display text based on status code
 */
function getStatusDisplayText(status) {
    const statusMap = {
        'to_do': 'To Do',
        'todo': 'To Do',
        'in_progress': 'In Progress',
        'in_review': 'In Review',
        'done': 'Done',
        'backlog': 'Backlog',
        'blocked': 'Blocked'
    };
    return statusMap[status] || status.charAt(0).toUpperCase() + status.slice(1).replace('_', ' ');
}

/**
 * Get status color based on status code
 */
function getStatusColor(status) {
    const colorMap = {
        'to_do': '#0d6efd',  // primary blue
        'todo': '#0d6efd',    // primary blue
        'in_progress': '#ffc107',  // warning yellow
        'in_review': '#6f42c1',    // purple
        'done': '#198754',     // success green
        'backlog': '#6c757d',  // secondary gray
        'blocked': '#dc3545'   // danger red
    };
    return colorMap[status] || '#6c757d';  // default to secondary gray
}

// getCookie function is already defined at the top of the file

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

// normalizeTaskType function is already defined at the top of the file

/**
 * Attach event listeners to status dropdown items
 */
function attachStatusDropdownListeners() {
    console.log('%c Attaching status dropdown listeners...', 'background: #9b59b6; color: white; padding: 3px; border-radius: 3px;');
    
    // Count status options before attaching listeners
    const statusOptions = document.querySelectorAll('.status-option');
    console.log(`Found ${statusOptions.length} status options`);
    
    if (statusOptions.length === 0) {
        console.error('No status options found! Check your HTML structure.');
        // Log the HTML structure to help debug
        console.log('Status dropdowns HTML:', document.querySelectorAll('.status-dropdown').length);
        document.querySelectorAll('.status-dropdown').forEach((dropdown, i) => {
            console.log(`Dropdown ${i} HTML:`, dropdown.innerHTML);
        });
        
        // Try to find dropdown items with a different selector
        const dropdownItems = document.querySelectorAll('.dropdown-item[data-status]');
        console.log(`Found ${dropdownItems.length} dropdown items with data-status attribute`);
        if (dropdownItems.length > 0) {
            console.log('Using alternative selector for status options');
            attachListenersToDropdownItems(dropdownItems);
            return;
        }
    }
    
    // Direct approach - add click handlers to all status options
    statusOptions.forEach((option, index) => {
        console.log(`Processing status option ${index}:`, option.textContent.trim());
        
        // Remove old event listeners by cloning and replacing
        const newOption = option.cloneNode(true);
        option.parentNode.replaceChild(newOption, option);
        
        // Add new click event listener with more detailed logging
        newOption.addEventListener('click', function(event) {
            console.log('%c STATUS OPTION CLICKED!', 'background: #e74c3c; color: white; padding: 10px; font-size: 16px; font-weight: bold;');
            console.log('Clicked option:', this.textContent.trim());
            console.log('Option element:', this);
            event.preventDefault();
            event.stopPropagation();
            
            // Get the clicked status
            const status = this.getAttribute('data-status');
            if (!status) {
                console.error('No status attribute found on clicked element');
                return;
            }
            
            // Find the task ID and type
            // First try the dropdown menu
            const dropdownMenu = this.closest('.dropdown-menu');
            let taskId = null;
            let taskType = null;
            
            if (dropdownMenu) {
                taskId = dropdownMenu.getAttribute('data-task-id');
                taskType = dropdownMenu.getAttribute('data-task-type');
                console.log(`From dropdown menu - Task ID: ${taskId}, Type: ${taskType}`);
            }
            
            // If not found, try the parent dropdown
            if (!taskId || !taskType) {
                const dropdown = this.closest('.status-dropdown');
                if (dropdown) {
                    taskId = dropdown.getAttribute('data-task-id');
                    taskType = dropdown.getAttribute('data-task-type');
                    console.log(`From dropdown - Task ID: ${taskId}, Type: ${taskType}`);
                }
            }
            
            // If still not found, try the parent row
            if (!taskId || !taskType) {
                const row = this.closest('tr');
                if (row) {
                    taskId = row.getAttribute('data-task-id');
                    taskType = row.getAttribute('data-task-type') || row.getAttribute('class').split(' ').find(c => c.includes('Task'));
                    console.log(`From row - Task ID: ${taskId}, Type: ${taskType}`);
                }
            }
            
            if (!taskId || !taskType || !status) {
                console.error('Missing required data for status update');
                alert('Error: Could not determine task information for status update');
                return;
            }
            
            // Update the task status
            updateTaskStatus(this, taskId, taskType, status);
        });
        
        // Ensure href is set to prevent navigation
        if (newOption.getAttribute('href') === '#') {
            newOption.setAttribute('href', 'javascript:void(0);');
        }
    });
    
    console.log('Status dropdown listeners attached');
}

/**
 * Handle status option click event
 */
function handleStatusOptionClick(event) {
    console.log('Status option clicked');
    event.preventDefault();
    event.stopPropagation();
    
    const statusOption = event.currentTarget;
    const dropdownMenu = statusOption.closest('.dropdown-menu');
    
    if (!dropdownMenu) {
        console.error('Could not find dropdown menu');
        return;
    }
    
    // Get status from the clicked option
    const status = statusOption.dataset.status;
    
    // Try to get task ID and type from dropdown menu first
    let taskId = dropdownMenu.dataset.taskId;
    let taskType = dropdownMenu.dataset.taskType;
    
    // If not found in dropdown menu, try to get from parent dropdown
    if (!taskId || !taskType) {
        const dropdown = dropdownMenu.closest('.status-dropdown');
        if (dropdown) {
            taskId = dropdown.dataset.taskId;
            taskType = dropdown.dataset.taskType;
        }
    }
    
    console.log(`Task ID: ${taskId}, Task Type: ${taskType}, Status: ${status}`);
    
    if (!taskId || !taskType || !status) {
        console.error('Missing required data attributes');
        return;
    }
    
    updateTaskStatus(statusOption, taskId, taskType, status);
}

/**
 * Attach listeners to dropdown items using alternative selector
 */
function attachListenersToDropdownItems(dropdownItems) {
    console.log('%c Attaching listeners to dropdown items with alternative selector', 'background: #3498db; color: white; padding: 5px;');
    
    dropdownItems.forEach((item, index) => {
        console.log(`Processing dropdown item ${index}:`, item.textContent.trim());
        
        // Remove old event listeners by cloning and replacing
        const newItem = item.cloneNode(true);
        item.parentNode.replaceChild(newItem, item);
        
        // Add new click event listener
        newItem.addEventListener('click', function(event) {
            console.log('%c DROPDOWN ITEM CLICKED!', 'background: #e74c3c; color: white; padding: 10px; font-size: 16px; font-weight: bold;');
            console.log('Clicked item:', this.textContent.trim());
            
            event.preventDefault();
            event.stopPropagation();
            
            // Extract task information
            const status = this.dataset.status;
            console.log('Status from data attribute:', status);
            
            // Find the dropdown parent
            const dropdown = this.closest('.dropdown');
            if (!dropdown) {
                console.error('Could not find parent dropdown');
                return;
            }
            
            const taskId = dropdown.dataset.taskId;
            const taskType = dropdown.dataset.taskType;
            
            console.log('Task ID from dropdown:', taskId);
            console.log('Task Type from dropdown:', taskType);
            
            if (!taskId || !taskType) {
                console.error('Missing task ID or type');
                return;
            }
            
            // Call updateTaskStatus with the extracted information
            updateTaskStatus(this, taskId, taskType, status);
        });
    });
}

/**
 * Update checkbox listeners after DataTables redraws
 */
function updateCheckboxListeners() {
    console.log('Updating checkbox listeners');
    
    // Update task checkboxes
    const taskCheckboxes = document.querySelectorAll('.task-checkbox');
    taskCheckboxes.forEach(checkbox => {
        // Remove old event listeners by cloning and replacing
        const newCheckbox = checkbox.cloneNode(true);
        checkbox.parentNode.replaceChild(newCheckbox, checkbox);
        
        // Add new change event listener
        newCheckbox.addEventListener('change', function() {
            updateSelectedCount();
        });
    });
    
    // Update select all checkbox
    const selectAllCheckbox = document.getElementById('selectAllTasks');
    if (selectAllCheckbox) {
        // Remove old event listeners by cloning and replacing
        const newSelectAll = selectAllCheckbox.cloneNode(true);
        selectAllCheckbox.parentNode.replaceChild(newSelectAll, selectAllCheckbox);
        
        // Add new change event listener
        newSelectAll.addEventListener('change', function() {
            const taskCheckboxes = document.querySelectorAll('.task-checkbox');
            taskCheckboxes.forEach(checkbox => {
                checkbox.checked = this.checked;
            });
            updateSelectedCount();
        });
    }
}

// showToast function is already defined at the top of the file
