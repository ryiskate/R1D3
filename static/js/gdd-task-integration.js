/**
 * GDD Task Integration
 * 
 * Handles the integration between GDD sections and tasks
 * Allows creating tasks linked to GDD sections and managing task-section relationships
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });
    
    // Smooth scrolling for section links
    document.querySelectorAll('.section-link').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop - 80,
                    behavior: 'smooth'
                });
                // Update URL without reloading page
                history.pushState(null, null, targetId);
            }
        });
    });
    
    // Highlight current section in TOC based on scroll position
    window.addEventListener('scroll', function() {
        const sections = document.querySelectorAll('.gdd-section');
        let currentSectionId = '';
        
        sections.forEach(section => {
            const sectionTop = section.offsetTop - 100;
            if (window.scrollY >= sectionTop) {
                currentSectionId = section.getAttribute('id');
            }
        });
        
        document.querySelectorAll('.section-link').forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === '#' + currentSectionId) {
                link.classList.add('active');
            }
        });
    });
    
    // Handle quick task creation from GDD sections
    document.querySelectorAll('.create-task-btn').forEach(button => {
        button.addEventListener('click', function() {
            const sectionId = this.getAttribute('data-section-id');
            const sectionTitle = this.getAttribute('data-section-title');
            
            // Populate the task modal with section info
            const modal = document.getElementById('createTaskModal');
            if (modal) {
                const sectionInput = modal.querySelector('#task-section-id');
                const taskTitleInput = modal.querySelector('#task-title');
                const sectionLabel = modal.querySelector('#section-title-display');
                
                if (sectionInput) sectionInput.value = sectionId;
                if (sectionLabel) sectionLabel.textContent = sectionTitle;
                if (taskTitleInput) taskTitleInput.value = `Implement: ${sectionTitle}`;
                
                // Show the modal
                const modalInstance = new bootstrap.Modal(modal);
                modalInstance.show();
            }
        });
    });
    
    // Handle task linking to sections
    document.querySelectorAll('.link-task-btn').forEach(button => {
        button.addEventListener('click', function() {
            const taskId = this.getAttribute('data-task-id');
            const taskTitle = this.getAttribute('data-task-title');
            
            // Populate the link task modal
            const modal = document.getElementById('linkTaskModal');
            if (modal) {
                const taskIdInput = modal.querySelector('#link-task-id');
                const taskTitleDisplay = modal.querySelector('#link-task-title');
                
                if (taskIdInput) taskIdInput.value = taskId;
                if (taskTitleDisplay) taskTitleDisplay.textContent = taskTitle;
                
                // Show the modal
                const modalInstance = new bootstrap.Modal(modal);
                modalInstance.show();
            }
        });
    });
    
    // Handle form submission for linking tasks to sections
    const linkTaskForm = document.getElementById('link-task-form');
    if (linkTaskForm) {
        linkTaskForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const taskId = this.querySelector('#link-task-id').value;
            const sectionId = this.querySelector('#link-section-select').value;
            const csrfToken = this.querySelector('[name="csrfmiddlewaretoken"]').value;
            
            fetch(`/games/tasks/${taskId}/link-gdd-section/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': csrfToken
                },
                body: `section_id=${sectionId}`
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    // Close modal and refresh page
                    const modal = document.getElementById('linkTaskModal');
                    const modalInstance = bootstrap.Modal.getInstance(modal);
                    modalInstance.hide();
                    
                    // Show success message
                    const toast = new bootstrap.Toast(document.getElementById('successToast'));
                    document.getElementById('toastMessage').textContent = data.message;
                    toast.show();
                    
                    // Reload page after a short delay
                    setTimeout(() => {
                        window.location.reload();
                    }, 1500);
                } else {
                    // Show error message
                    const errorMsg = document.getElementById('link-task-error');
                    errorMsg.textContent = data.message || 'An error occurred';
                    errorMsg.style.display = 'block';
                }
            })
            .catch(error => {
                console.error('Error:', error);
                const errorMsg = document.getElementById('link-task-error');
                errorMsg.textContent = 'Network error occurred';
                errorMsg.style.display = 'block';
            });
        });
    }
});
