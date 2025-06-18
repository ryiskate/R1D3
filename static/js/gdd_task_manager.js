/**
 * GDD Task Manager
 * Handles task management functionality in the GDD interface
 */

class GDDTaskManager {
    constructor() {
        this.initFilterButtons();
        this.initStatusSelects();
        this.initTaskSelection();
        this.initHoursInputs();
        this.setupBatchUpdate();
    }

    /**
     * Initialize task filtering functionality
     */
    initFilterButtons() {
        document.querySelectorAll('.filter-btn').forEach(button => {
            button.addEventListener('click', (e) => {
                const filter = e.target.getAttribute('data-filter');
                
                // Update active button
                document.querySelectorAll('.filter-btn').forEach(btn => {
                    btn.classList.remove('active');
                });
                e.target.classList.add('active');
                
                // Filter tasks
                document.querySelectorAll('.task-row').forEach(row => {
                    if (filter === 'all' || row.getAttribute('data-status') === filter) {
                        row.style.display = '';
                    } else {
                        row.style.display = 'none';
                    }
                });
            });
        });
    }

    /**
     * Initialize status select change handlers
     */
    initStatusSelects() {
        document.querySelectorAll('.status-select').forEach(select => {
            select.addEventListener('change', (e) => {
                const form = e.target.closest('form');
                const taskId = e.target.getAttribute('data-task-id');
                
                // Submit form via AJAX
                const formData = new FormData(form);
                
                fetch(form.action, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Update row status attribute
                        const row = e.target.closest('.task-row');
                        row.setAttribute('data-status', data.new_status);
                        
                        // Show success notification
                        this.showToast(`Task status updated to ${data.status_display}`, 'success');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    this.showToast('Error updating task status', 'danger');
                });
            });
        });
    }

    /**
     * Initialize task selection functionality
     */
    initTaskSelection() {
        const selectAllCheckbox = document.getElementById('selectAllTasks');
        const taskCheckboxes = document.querySelectorAll('.task-checkbox');
        const batchUpdateBtn = document.getElementById('batchUpdateBtn');
        const selectedTaskCount = document.getElementById('selectedTaskCount');
        
        if (!selectAllCheckbox) return;
        
        const updateSelectedCount = () => {
            const selectedCount = document.querySelectorAll('.task-checkbox:checked').length;
            selectedTaskCount.textContent = selectedCount;
            batchUpdateBtn.disabled = selectedCount === 0;
        };
        
        selectAllCheckbox.addEventListener('change', (e) => {
            taskCheckboxes.forEach(checkbox => {
                checkbox.checked = e.target.checked;
            });
            updateSelectedCount();
        });
        
        taskCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', () => {
                updateSelectedCount();
                
                // Update "select all" checkbox
                selectAllCheckbox.checked = document.querySelectorAll('.task-checkbox:checked').length === taskCheckboxes.length;
            });
        });
    }

    /**
     * Initialize hours input form submission
     */
    initHoursInputs() {
        document.querySelectorAll('.task-hours-form').forEach(form => {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                
                const formData = new FormData(form);
                
                fetch(form.action, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        this.showToast(`Task hours updated to ${data.actual_hours}`, 'success');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    this.showToast('Error updating task hours', 'danger');
                });
            });
        });
    }

    /**
     * Set up batch update functionality
     */
    setupBatchUpdate() {
        const batchUpdateBtn = document.getElementById('batchUpdateBtn');
        const batchTaskForm = document.getElementById('batchTaskForm');
        
        if (!batchUpdateBtn || !batchTaskForm) return;
        
        batchUpdateBtn.addEventListener('click', () => {
            const modal = new bootstrap.Modal(document.getElementById('batchUpdateModal'));
            modal.show();
        });
        
        batchTaskForm.addEventListener('submit', (e) => {
            e.preventDefault();
            
            const formData = new FormData(batchTaskForm);
            
            fetch(batchTaskForm.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Close modal
                    const modal = bootstrap.Modal.getInstance(document.getElementById('batchUpdateModal'));
                    modal.hide();
                    
                    // Update UI for affected tasks
                    const newStatus = formData.get('status');
                    const taskIds = formData.getAll('task_ids');
                    
                    taskIds.forEach(taskId => {
                        const row = document.querySelector(`.task-row[data-task-id="${taskId}"]`);
                        if (row) {
                            row.setAttribute('data-status', newStatus);
                            const statusSelect = row.querySelector('.status-select');
                            if (statusSelect) {
                                statusSelect.value = newStatus;
                            }
                        }
                    });
                    
                    // Show success notification
                    this.showToast(data.message, 'success');
                    
                    // Uncheck all checkboxes
                    document.querySelectorAll('.task-checkbox').forEach(checkbox => {
                        checkbox.checked = false;
                    });
                    document.getElementById('selectAllTasks').checked = false;
                    document.getElementById('batchUpdateBtn').disabled = true;
                }
            })
            .catch(error => {
                console.error('Error:', error);
                this.showToast('Error updating tasks', 'danger');
            });
        });
    }

    /**
     * Show a toast notification
     * @param {string} message - Message to display
     * @param {string} type - Bootstrap color type (success, danger, etc.)
     */
    showToast(message, type = 'success') {
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type}`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        `;
        
        // Add toast container if it doesn't exist
        let toastContainer = document.querySelector('.toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
            document.body.appendChild(toastContainer);
        }
        
        toastContainer.appendChild(toast);
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
        
        setTimeout(() => {
            toast.remove();
        }, 3000);
    }
}

// Initialize task manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new GDDTaskManager();
});
