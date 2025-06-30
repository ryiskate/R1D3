/**
 * Education Task Delete Handler
 * 
 * Adds Bootstrap modal confirmation dialog to education task delete buttons
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('Education Task Delete Handler initialized');
    
    // Track initialization to prevent duplicate handlers
    if (window.educationTaskDeleteHandlerInitialized) {
        console.log('Education Task Delete Handler already initialized, skipping');
        return;
    }
    window.educationTaskDeleteHandlerInitialized = true;
    
    // Find all delete buttons for education tasks
    const deleteButtons = document.querySelectorAll('a.btn-outline-danger[href*="task_delete"]');
    
    console.log(`Found ${deleteButtons.length} education task delete buttons`);
    
    // Check if the modal already exists in the DOM
    let deleteModal = document.getElementById('deleteTaskModal');
    let modalInitialized = false;
    
    // If the modal doesn't exist, load it via AJAX
    if (!deleteModal) {
        console.log('Delete modal not found in DOM, checking if it needs to be loaded');
        
        // Check if we're on the education tasks page
        if (window.location.pathname.includes('/education/tasks')) {
            console.log('On education tasks page, modal should be included in the template');
        } else {
            console.log('Not on education tasks page, modal may need to be loaded dynamically');
            // This would be the place to dynamically load the modal if needed
        }
    } else {
        console.log('Delete modal found in DOM');
        modalInitialized = true;
    }
    
    deleteButtons.forEach((button, index) => {
        console.log(`Processing education delete button ${index + 1}/${deleteButtons.length}`);
        
        // Add a distinctive class for styling and identification
        button.classList.add('education-delete-btn');
        
        // Get task information
        const taskRow = button.closest('tr');
        let taskTitle = 'this task';
        
        // Try to find the task title in the row
        if (taskRow) {
            const titleCell = taskRow.querySelector('td:first-child');
            if (titleCell) {
                taskTitle = titleCell.textContent.trim();
            }
        }
        
        // Store the original href
        const originalHref = button.getAttribute('href');
        
        // Replace the href with javascript:void(0) to prevent direct navigation
        button.setAttribute('href', 'javascript:void(0)');
        
        // Add click event listener to show confirmation dialog
        button.addEventListener('click', function(event) {
            event.preventDefault();
            
            // If we have a modal, use it
            if (deleteModal) {
                // Set the task title in the modal
                const titleSpan = deleteModal.querySelector('#deleteTaskTitle');
                if (titleSpan) {
                    titleSpan.textContent = taskTitle;
                }
                
                // Set the confirm button href
                const confirmBtn = deleteModal.querySelector('#confirmDeleteBtn');
                if (confirmBtn) {
                    confirmBtn.setAttribute('href', originalHref);
                }
                
                // Show the modal
                const bsModal = new bootstrap.Modal(deleteModal);
                bsModal.show();
            } else {
                // Fallback to browser confirm dialog if modal not available
                if (confirm(`Are you sure you want to delete the task "${taskTitle}"? This action cannot be undone.`)) {
                    window.location.href = originalHref;
                }
            }
        });
    });
});
