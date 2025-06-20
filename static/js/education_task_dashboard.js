document.addEventListener('DOMContentLoaded', function() {
    console.log('Education Tasks Dashboard loaded');
    
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[title]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize DataTable
    const taskTable = $('#taskTable').DataTable({
        "pageLength": 25,
        "order": [],
        "columnDefs": [
            { "orderable": false, "targets": [0, 8] }
        ],
        "language": {
            "search": "Quick search:",
            "emptyTable": "No education tasks found"
        }
    });
    
    // Handle select all checkbox
    $('#selectAllTasks').on('change', function() {
        $('.task-checkbox').prop('checked', $(this).prop('checked'));
        updateBatchButton();
    });
    
    // Handle individual checkboxes
    $(document).on('change', '.task-checkbox', function() {
        updateBatchButton();
    });
    
    // Update batch button state
    function updateBatchButton() {
        const checkedCount = $('.task-checkbox:checked').length;
        $('#batchUpdateBtn').prop('disabled', checkedCount === 0);
    }
    
    // Open batch update modal
    $('#batchUpdateBtn').on('click', function() {
        const selectedTaskIds = [];
        $('.task-checkbox:checked').each(function() {
            selectedTaskIds.push($(this).data('task-id'));
        });
        $('#batchTaskIds').val(JSON.stringify(selectedTaskIds));
        $('#batchUpdateModal').modal('show');
    });
    
    // Apply filters
    $('#applyFiltersBtn').on('click', function() {
        $('#filterForm').submit();
    });
    
    // Apply batch updates
    $('#applyBatchUpdateBtn').on('click', function() {
        const formData = new FormData($('#batchUpdateForm')[0]);
        const taskIds = JSON.parse($('#batchTaskIds').val());
        
        // Add CSRF token
        formData.append('csrfmiddlewaretoken', getCookie('csrftoken'));
        
        $.ajax({
            url: batchUpdateUrl,
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                $('#batchUpdateModal').modal('hide');
                showToast('Success', 'Tasks updated successfully', 'success');
                setTimeout(function() {
                    window.location.reload();
                }, 1000);
            },
            error: function(xhr) {
                showToast('Error', 'Failed to update tasks', 'error');
            }
        });
    });
    
    // Handle due date and clear due date interaction
    $('#batchDueDate').on('change', function() {
        if ($(this).val()) {
            $('#clearDueDate').prop('checked', false);
        }
    });
    
    $('#clearDueDate').on('change', function() {
        if ($(this).prop('checked')) {
            $('#batchDueDate').val('');
        }
    });
    
    // Helper function to show toast notifications
    function showToast(title, message, type = 'info') {
        const toast = $(`
            <div class="toast" role="alert" aria-live="assertive" aria-atomic="true" data-bs-delay="3000">
                <div class="toast-header bg-${type} text-white">
                    <strong class="me-auto">${title}</strong>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
                <div class="toast-body">
                    ${message}
                </div>
            </div>
        `);
        
        $('.toast-container').append(toast);
        const bsToast = new bootstrap.Toast(toast[0]);
        bsToast.show();
        
        toast.on('hidden.bs.toast', function() {
            $(this).remove();
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
});
