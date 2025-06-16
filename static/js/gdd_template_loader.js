/**
 * GDD Template Loader
 * This script loads the GDD template content into the HTML editor when the user clicks the "Load Template" button.
 */
document.addEventListener('DOMContentLoaded', function() {
    // Get the load template button
    const loadTemplateBtn = document.getElementById('load-template-btn');
    
    if (loadTemplateBtn) {
        loadTemplateBtn.addEventListener('click', function() {
            // Show loading state
            loadTemplateBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Loading...';
            loadTemplateBtn.disabled = true;
            
            // Fetch the template content from the static file
            fetch('/static/templates/gdd_template.html')
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Failed to load template');
                    }
                    return response.text();
                })
                .then(templateContent => {
                    // Get the Quill editor instance
                    const quill = Quill.find(document.getElementById('html-editor'));
                    
                    // Set the template content in the editor
                    quill.root.innerHTML = templateContent;
                    
                    // Update the hidden input with the template content
                    document.getElementById('html_content_input').value = templateContent;
                    
                    // Show success message
                    const alertContainer = document.createElement('div');
                    alertContainer.className = 'alert alert-success alert-dismissible fade show mt-3';
                    alertContainer.innerHTML = `
                        <strong>Success!</strong> GDD template loaded successfully.
                        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                    `;
                    document.getElementById('html-editor-container').prepend(alertContainer);
                    
                    // Reset button state
                    loadTemplateBtn.innerHTML = 'Load Template';
                    loadTemplateBtn.disabled = false;
                    
                    // Auto-extract sections after loading the template
                    document.getElementById('extract-sections-btn').click();
                })
                .catch(error => {
                    console.error('Error loading template:', error);
                    
                    // Show error message
                    const alertContainer = document.createElement('div');
                    alertContainer.className = 'alert alert-danger alert-dismissible fade show mt-3';
                    alertContainer.innerHTML = `
                        <strong>Error!</strong> Failed to load GDD template. Please try again.
                        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                    `;
                    document.getElementById('html-editor-container').prepend(alertContainer);
                    
                    // Reset button state
                    loadTemplateBtn.innerHTML = 'Load Template';
                    loadTemplateBtn.disabled = false;
                });
        });
    }
});
