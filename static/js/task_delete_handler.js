/**
 * Task Delete Handler
 * 
 * Enhances the task delete functionality by ensuring proper URL construction
 * and providing feedback to the user.
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('Task Delete Handler initialized');
    
    // Track initialization to prevent duplicate handlers
    if (window.taskDeleteHandlerInitialized) {
        console.log('Task Delete Handler already initialized, skipping');
        return;
    }
    window.taskDeleteHandlerInitialized = true;
    // Find all delete buttons for tasks
    const deleteButtons = document.querySelectorAll('a[data-task-id][title="Delete"]');
    
    console.log(`Found ${deleteButtons.length} delete buttons`);
    
    deleteButtons.forEach((button, index) => {
        console.log(`Processing delete button ${index + 1}/${deleteButtons.length}`);
        
        // Add a distinctive class for styling and identification
        button.classList.add('enhanced-delete-btn');
        
        button.addEventListener('click', function(event) {
            // Get the task ID from the data attribute
            const taskId = this.getAttribute('data-task-id');
            
            if (!taskId) {
                console.error('No task ID found for delete button');
                return;
            }
            
            console.log(`Delete button clicked for task ID: ${taskId}`);
            
            // Verify the URL is correctly formed
            const href = this.getAttribute('href');
            const expectedUrl = `/games/tasks/${taskId}/delete/`;
            
            // If the URL doesn't match the expected format, correct it
            if (href !== expectedUrl) {
                console.log(`Correcting delete URL from ${href} to ${expectedUrl}`);
                this.setAttribute('href', expectedUrl);
                
                // Add visual feedback that the URL was corrected
                this.style.border = '2px solid green';
                this.setAttribute('title', 'Delete (URL corrected)');
                
                // Optional: Show a tooltip or message to the user
                try {
                    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
                        new bootstrap.Tooltip(this, {
                            title: 'URL corrected for proper deletion',
                            trigger: 'manual'
                        }).show();
                        
                        // Hide tooltip after 2 seconds
                        setTimeout(() => {
                            bootstrap.Tooltip.getInstance(this)?.hide();
                        }, 2000);
                    }
                } catch (error) {
                    console.warn('Could not show tooltip:', error);
                }
            } else {
                console.log('Delete URL is correctly formatted');
            }
        });
    });
    
    // Also enhance the edit buttons for consistency
    const editButtons = document.querySelectorAll('a[data-task-id][title="Edit"]');
    
    console.log(`Found ${editButtons.length} edit buttons`);
    
    editButtons.forEach((button, index) => {
        console.log(`Processing edit button ${index + 1}/${editButtons.length}`);
        
        // Add a distinctive class for styling and identification
        button.classList.add('enhanced-edit-btn');
        
        button.addEventListener('click', function(event) {
            // Get the task ID from the data attribute
            const taskId = this.getAttribute('data-task-id');
            
            if (!taskId) {
                console.error('No task ID found for edit button');
                return;
            }
            
            console.log(`Edit button clicked for task ID: ${taskId}`);
            
            // Verify the URL is correctly formed
            const href = this.getAttribute('href');
            const expectedUrl = `/games/tasks/${taskId}/update/`;
            
            // If the URL doesn't match the expected format, correct it
            if (href !== expectedUrl) {
                console.log(`Correcting edit URL from ${href} to ${expectedUrl}`);
                this.setAttribute('href', expectedUrl);
                
                // Add visual feedback that the URL was corrected
                this.style.border = '2px solid blue';
                this.setAttribute('title', 'Edit (URL corrected)');
            } else {
                console.log('Edit URL is correctly formatted');
            }
        });
    });
    
    // Add a small helper function to check all task-related URLs on the page
    window.checkAllTaskUrls = function() {
        console.log('Checking all task URLs on the page...');
        
        const allTaskLinks = document.querySelectorAll('a[href*="/tasks/"]');
        console.log(`Found ${allTaskLinks.length} task-related links`);
        
        allTaskLinks.forEach((link, index) => {
            const href = link.getAttribute('href');
            console.log(`${index + 1}. ${href}`);
        });
        
        return 'URL check complete. See console for details.';
    };
    
    // Run the check automatically if in debug mode
    if (window.location.search.includes('debug=true')) {
        console.log('Debug mode detected, running URL check...');
        setTimeout(window.checkAllTaskUrls, 1000);
    }
});
