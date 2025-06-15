/**
 * GDD Detail Page JavaScript
 * Handles table of contents generation, task badges, and section highlighting
 */

function initGddDetailPage(options) {
    // Options should contain:
    // - sectionsJson: array of section objects
    // - sectionsWithTasksJson: object mapping section IDs to task arrays
    // - canCreateTask: boolean indicating if user can create tasks
    // - canLinkTasks: boolean indicating if user can link tasks
    
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Generate table of contents from HTML content
    var gddContent = document.getElementById('gdd-html-content');
    var tocContainer = document.getElementById('toc-container');
    
    if (gddContent && tocContainer) {
        // Find all headings
        var headings = gddContent.querySelectorAll('h1, h2, h3');
        
        if (headings.length > 0) {
            // Create TOC list
            var tocList = document.createElement('ul');
            tocList.className = 'nav flex-column toc-list';
            
            // Process each heading
            headings.forEach(function(heading) {
                // Create unique ID for the heading if it doesn't have one
                if (!heading.id) {
                    heading.id = 'heading-' + heading.textContent.trim().toLowerCase().replace(/\s+/g, '-');
                }
                
                // Create TOC item
                var tocItem = document.createElement('li');
                tocItem.className = 'nav-item';
                
                // Create link
                var link = document.createElement('a');
                link.className = 'nav-link toc-link';
                if (heading.tagName === 'H1') {
                    link.className += ' toc-h1';
                } else if (heading.tagName === 'H2') {
                    link.className += ' toc-h2';
                } else if (heading.tagName === 'H3') {
                    link.className += ' toc-h3';
                }
                link.href = '#' + heading.id;
                link.textContent = heading.textContent;
                
                tocItem.appendChild(link);
                tocList.appendChild(tocItem);
                
                // Create badge container for tasks
                var badgeContainer = document.createElement('div');
                badgeContainer.className = 'badge-container';
                
                // Find section by heading text
                var sectionTitle = heading.textContent.trim();
                var section = options.sectionsJson.find(function(s) { 
                    return s.title === sectionTitle; 
                });
                
                if (section) {
                    // Create task count badge
                    var tasks = (options.sectionsWithTasksJson)[section.id] || [];
                    var badge = document.createElement('span');
                    badge.className = 'badge bg-info task-badge';
                    badge.setAttribute('data-bs-toggle', 'tooltip');
                    badge.setAttribute('data-bs-html', 'true');
                    
                    var tooltipContent = '';
                    if (tasks.length > 0) {
                        tasks.forEach(function(task) {
                            tooltipContent += '<div><strong>' + task.title + '</strong></div>';
                            tooltipContent += '<div class="text-muted small">' + task.status_display + '</div>';
                        });
                    } else {
                        tooltipContent = 'No tasks linked to this section';
                    }
                    
                    badge.setAttribute('title', tooltipContent);
                    badge.innerHTML = '<i class="bi bi-list-task"></i> ' + tasks.length;
                    badgeContainer.appendChild(badge);
                    
                    // Create task button if user has permission
                    if (options.canCreateTask) {
                        var createBtn = document.createElement('button');
                        createBtn.className = 'btn btn-sm btn-outline-primary task-create-btn';
                        createBtn.setAttribute('data-bs-toggle', 'modal');
                        createBtn.setAttribute('data-bs-target', '#createTaskModal');
                        createBtn.setAttribute('data-section-id', section.id);
                        createBtn.setAttribute('data-section-title', section.title);
                        createBtn.setAttribute('title', 'Create task for this section');
                        createBtn.innerHTML = '<i class="bi bi-plus-lg"></i>';
                        badgeContainer.appendChild(createBtn);
                        
                        // Add event listener directly to avoid delegation issues
                        createBtn.addEventListener('click', function() {
                            var sectionId = this.getAttribute('data-section-id');
                            var sectionTitle = this.getAttribute('data-section-title');
                            
                            var sectionIdInput = document.getElementById('task-section-id');
                            var sectionTitleDisplay = document.getElementById('section-title-display');
                            var taskTitleInput = document.getElementById('task-title');
                            
                            if (sectionIdInput) sectionIdInput.value = sectionId;
                            if (sectionTitleDisplay) sectionTitleDisplay.textContent = sectionTitle;
                            if (taskTitleInput) taskTitleInput.value = 'Implement: ' + sectionTitle;
                        });
                    }
                    
                    // Convert heading to a flex container
                    heading.style.display = 'flex';
                    heading.style.justifyContent = 'space-between';
                    heading.style.alignItems = 'center';
                    
                    // Create a span for the heading text
                    var headingText = document.createElement('span');
                    headingText.textContent = heading.textContent;
                    
                    // Clear the heading and add the new elements
                    heading.textContent = '';
                    heading.appendChild(headingText);
                    heading.appendChild(badgeContainer);
                }
            });
            
            // Initialize tooltips for dynamically added badges
            var newTooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
            newTooltipTriggerList.map(function(tooltipTriggerEl) {
                return new bootstrap.Tooltip(tooltipTriggerEl);
            });
            
            // Add TOC to container
            tocContainer.appendChild(tocList);
            
            // Add smooth scrolling to TOC links
            document.querySelectorAll('.toc-link').forEach(function(link) {
                link.addEventListener('click', function(e) {
                    e.preventDefault();
                    var targetId = this.getAttribute('href').substring(1);
                    var targetElement = document.getElementById(targetId);
                    
                    if (targetElement) {
                        window.scrollTo({
                            top: targetElement.offsetTop - 70,
                            behavior: 'smooth'
                        });
                    }
                });
            });
            
            // Highlight active section on scroll
            window.addEventListener('scroll', function() {
                var scrollPosition = window.scrollY;
                
                // Find the current heading
                var currentHeading = null;
                headings.forEach(function(heading) {
                    if (heading.offsetTop - 100 <= scrollPosition) {
                        currentHeading = heading;
                    }
                });
                
                if (currentHeading) {
                    // Remove active class from all links
                    document.querySelectorAll('.toc-link').forEach(function(link) {
                        link.classList.remove('active');
                    });
                    
                    var activeLink = document.querySelector('.toc-link[href="#' + currentHeading.id + '"]');
                    if (activeLink) {
                        activeLink.classList.add('active');
                    }
                }
            });
        }
    }
}

// Handle task creation modal
document.addEventListener('DOMContentLoaded', function() {
    var createTaskModal = document.getElementById('createTaskModal');
    if (createTaskModal) {
        createTaskModal.addEventListener('show.bs.modal', function(event) {
            var button = event.relatedTarget;
            var sectionId = button.getAttribute('data-section-id');
            var sectionTitle = button.getAttribute('data-section-title');
            
            var sectionIdInput = document.getElementById('task-section-id');
            var sectionTitleDisplay = document.getElementById('section-title-display');
            var taskTitleInput = document.getElementById('task-title');
            
            if (sectionIdInput) sectionIdInput.value = sectionId;
            if (sectionTitleDisplay) sectionTitleDisplay.textContent = sectionTitle;
            if (taskTitleInput) taskTitleInput.value = 'Implement: ' + sectionTitle;
        });
    }
    
    // Handle link task modal
    var linkTaskModal = document.getElementById('linkTaskModal');
    if (linkTaskModal) {
        linkTaskModal.addEventListener('show.bs.modal', function(event) {
            var button = event.relatedTarget;
            var taskId = button.getAttribute('data-task-id');
            var taskTitle = button.getAttribute('data-task-title');
            
            var taskIdInput = document.getElementById('link-task-id');
            var taskTitleDisplay = document.getElementById('link-task-title');
            
            if (taskIdInput) taskIdInput.value = taskId;
            if (taskTitleDisplay) taskTitleDisplay.textContent = taskTitle;
        });
    }
    
    // Handle form submission for linking tasks to sections
    var linkTaskForm = document.getElementById('link-task-form');
    if (linkTaskForm) {
        linkTaskForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            var taskId = this.querySelector('#link-task-id').value;
            var sectionId = this.querySelector('#link-section-select').value;
            var csrfToken = this.querySelector('[name="csrfmiddlewaretoken"]').value;
            
            fetch('/games/tasks/' + taskId + '/link-gdd-section/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': csrfToken
                },
                body: 'section_id=' + sectionId
            })
            .then(function(response) { return response.json(); })
            .then(function(data) {
                if (data.status === 'success') {
                    // Close modal
                    var modal = document.getElementById('linkTaskModal');
                    var modalInstance = bootstrap.Modal.getInstance(modal);
                    modalInstance.hide();
                    
                    // Show success message
                    var toast = new bootstrap.Toast(document.getElementById('successToast'));
                    document.getElementById('toastMessage').textContent = data.message;
                    toast.show();
                    
                    // Reload page after a short delay
                    setTimeout(function() {
                        window.location.reload();
                    }, 1500);
                } else {
                    // Show error message
                    var errorMsg = document.getElementById('link-task-error');
                    errorMsg.textContent = data.message || 'An error occurred';
                    errorMsg.style.display = 'block';
                }
            })
            .catch(function(error) {
                console.error('Error:', error);
                var errorMsg = document.getElementById('link-task-error');
                errorMsg.textContent = 'Network error occurred';
                errorMsg.style.display = 'block';
            });
        });
    }
});
