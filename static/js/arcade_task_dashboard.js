document.addEventListener('DOMContentLoaded', function() {
    // Initialize variables
    const selectAllCheckbox = document.getElementById('selectAllTasks');
    const taskCheckboxes = document.querySelectorAll('.task-checkbox');
    const applyFiltersBtn = document.getElementById('applyFiltersBtn');
    const applyBatchUpdateBtn = document.getElementById('applyBatchUpdateBtn');
    const noTasksSelectedAlert = document.getElementById('noTasksSelectedAlert');
    
    // Batch update form elements
    const updateStatus = document.getElementById('updateStatus');
    const updatePriority = document.getElementById('updatePriority');
    const updateAssignee = document.getElementById('updateAssignee');
    const updateDueDate = document.getElementById('updateDueDate');
    const updateMachineId = document.getElementById('updateMachineId');
    const updateLocation = document.getElementById('updateLocation');
    const updateMaintenanceType = document.getElementById('updateMaintenanceType');
    
    const batchStatus = document.getElementById('batchStatus');
    const batchPriority = document.getElementById('batchPriority');
    const batchAssignee = document.getElementById('batchAssignee');
    const batchDueDate = document.getElementById('batchDueDate');
    const batchMachineId = document.getElementById('batchMachineId');
    const batchLocation = document.getElementById('batchLocation');
    const batchMaintenanceType = document.getElementById('batchMaintenanceType');
    const removeDueDate = document.getElementById('removeDueDate');
    
    // Set up the select all functionality
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function() {
            taskCheckboxes.forEach(checkbox => {
                checkbox.checked = selectAllCheckbox.checked;
            });
        });
    }
    
    // Apply filters button
    if (applyFiltersBtn) {
        applyFiltersBtn.addEventListener('click', function() {
            document.getElementById('filterForm').submit();
        });
    }
    
    // Toggle batch update form fields based on checkboxes
    if (updateStatus) {
        updateStatus.addEventListener('change', function() {
            batchStatus.disabled = !this.checked;
        });
    }
    
    if (updatePriority) {
        updatePriority.addEventListener('change', function() {
            batchPriority.disabled = !this.checked;
        });
    }
    
    if (updateAssignee) {
        updateAssignee.addEventListener('change', function() {
            batchAssignee.disabled = !this.checked;
        });
    }
    
    if (updateDueDate) {
        updateDueDate.addEventListener('change', function() {
            batchDueDate.disabled = !this.checked;
            removeDueDate.disabled = !this.checked;
            if (!this.checked) {
                removeDueDate.checked = false;
            }
        });
    }
    
    if (updateMachineId) {
        updateMachineId.addEventListener('change', function() {
            batchMachineId.disabled = !this.checked;
        });
    }
    
    if (updateLocation) {
        updateLocation.addEventListener('change', function() {
            batchLocation.disabled = !this.checked;
        });
    }
    
    if (updateMaintenanceType) {
        updateMaintenanceType.addEventListener('change', function() {
            batchMaintenanceType.disabled = !this.checked;
        });
    }
    
    if (removeDueDate) {
        removeDueDate.addEventListener('change', function() {
            if (this.checked) {
                batchDueDate.disabled = true;
                batchDueDate.value = '';
            } else {
                batchDueDate.disabled = !updateDueDate.checked;
            }
        });
    }
    
    // Apply batch updates
    if (applyBatchUpdateBtn) {
        applyBatchUpdateBtn.addEventListener('click', function() {
            // Get selected task IDs
            const selectedTaskIds = [];
            taskCheckboxes.forEach(checkbox => {
                if (checkbox.checked) {
                    selectedTaskIds.push(checkbox.value);
                }
            });
            
            // Check if any tasks are selected
            if (selectedTaskIds.length === 0) {
                noTasksSelectedAlert.classList.remove('d-none');
                return;
            } else {
                noTasksSelectedAlert.classList.add('d-none');
            }
            
            // Prepare update data
            const updateData = {};
            
            if (updateStatus.checked && batchStatus.value) {
                updateData.status = batchStatus.value;
            }
            
            if (updatePriority.checked && batchPriority.value) {
                updateData.priority = batchPriority.value;
            }
            
            if (updateAssignee.checked) {
                updateData.assigned_to = batchAssignee.value;
            }
            
            if (updateDueDate.checked) {
                if (removeDueDate.checked) {
                    updateData.due_date = 'no_date';
                } else if (batchDueDate.value) {
                    updateData.due_date = batchDueDate.value;
                }
            }
            
            if (updateMachineId.checked && batchMachineId.value) {
                updateData.machine_id = batchMachineId.value;
            }
            
            if (updateLocation.checked && batchLocation.value) {
                updateData.location = batchLocation.value;
            }
            
            if (updateMaintenanceType.checked && batchMaintenanceType.value) {
                updateData.maintenance_type = batchMaintenanceType.value;
            }
            
            // Check if any update fields are selected
            if (Object.keys(updateData).length === 0) {
                showToast('Please select at least one field to update', 'warning');
                return;
            }
            
            // Send AJAX request
            fetch(batchUpdateUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    task_ids: selectedTaskIds,
                    update_data: updateData
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showToast(data.message, 'success');
                    // Reload page to show updated tasks
                    setTimeout(() => {
                        window.location.reload();
                    }, 1500);
                } else {
                    showToast(data.message, 'error');
                }
            })
            .catch(error => {
                showToast('An error occurred while updating tasks', 'error');
                console.error('Error:', error);
            });
        });
    }
    
    // Helper function to get CSRF token
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
    
    // Toast notification function
    function showToast(message, type) {
        // Check if toastr is available
        if (typeof toastr !== 'undefined') {
            toastr.options = {
                closeButton: true,
                progressBar: true,
                positionClass: 'toast-top-right',
                timeOut: 5000
            };
            
            switch (type) {
                case 'success':
                    toastr.success(message);
                    break;
                case 'error':
                    toastr.error(message);
                    break;
                case 'warning':
                    toastr.warning(message);
                    break;
                default:
                    toastr.info(message);
            }
        } else {
            // Fallback if toastr is not available
            alert(message);
        }
    }
});
