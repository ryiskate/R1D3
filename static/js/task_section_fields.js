/**
 * Task Section Fields Manager
 * 
 * This script handles the dynamic display of section-specific fields in the task form
 * based on the selected company section.
 */
document.addEventListener('DOMContentLoaded', function() {
    // Get the company section select element
    const companySectionSelect = document.getElementById('id_company_section');
    if (!companySectionSelect) return;
    
    // Map of section IDs to their fieldset elements
    const sectionFields = {
        'game_development': document.getElementById('game_development_fields'),
        'education': document.getElementById('education_fields'),
        'arcade': document.getElementById('arcade_fields'),
        'marketing': document.getElementById('marketing_fields'),
        'research': document.getElementById('research_fields'),
        'finance': document.getElementById('finance_fields'),
        'hr': document.getElementById('hr_fields'),
        'it': document.getElementById('it_fields'),
        'other': document.getElementById('other_fields')
    };
    
    // Get the task_type field container - we'll handle it specially
    const taskTypeField = document.getElementById('id_task_type');
    const taskTypeContainer = taskTypeField ? taskTypeField.closest('.mb-3') : null;
    
    /**
     * Updates the visibility of section-specific fields based on the selected company section
     */
    function updateSectionFields() {
        const selectedSection = companySectionSelect.value;
        
        // Hide all section fields
        Object.values(sectionFields).forEach(fieldset => {
            if (fieldset) fieldset.classList.add('d-none');
        });
        
        // Show selected section fields
        if (sectionFields[selectedSection]) {
            sectionFields[selectedSection].classList.remove('d-none');
            
            // Add a visual indicator that this section is active
            sectionFields[selectedSection].classList.add('border-primary');
            
            // Update the help text to show section-specific guidance
            const helpText = document.getElementById('section-help-text');
            if (helpText) {
                switch (selectedSection) {
                    case 'game_development':
                        helpText.innerHTML = 'Game Development tasks can be linked to GDD sections and specific features.';
                        break;
                    case 'education':
                        helpText.innerHTML = 'Education tasks relate to courses, learning materials, and target audiences.';
                        break;
                    case 'arcade':
                        helpText.innerHTML = 'Arcade tasks track machine maintenance, locations, and service types.';
                        break;
                    case 'marketing':
                        helpText.innerHTML = 'Marketing tasks are organized by campaigns, channels, and target metrics.';
                        break;
                    case 'research':
                        helpText.innerHTML = 'Research tasks track experiments, hypotheses, and research areas.';
                        break;
                    default:
                        helpText.innerHTML = 'Select the appropriate company section to see section-specific fields.';
                }
            }
        }
    }
    
    // Set initial state
    updateSectionFields();
    
    // Update on change
    companySectionSelect.addEventListener('change', updateSectionFields);
    
    // Add validation for section-specific required fields
    const form = companySectionSelect.closest('form');
    if (form) {
        form.addEventListener('submit', function(e) {
            const selectedSection = companySectionSelect.value;
            let isValid = true;
            
            // Example: For game development, ensure GDD section is selected when available
            if (selectedSection === 'game_development') {
                const gddSectionSelect = document.getElementById('id_gdd_section');
                if (gddSectionSelect && gddSectionSelect.options.length > 1 && !gddSectionSelect.value) {
                    const errorMsg = document.createElement('div');
                    errorMsg.className = 'invalid-feedback d-block';
                    errorMsg.textContent = 'Please select a GDD section for this game development task.';
                    gddSectionSelect.parentNode.appendChild(errorMsg);
                    isValid = false;
                }
            }
            
            if (!isValid) {
                e.preventDefault();
            }
        });
    }
});
