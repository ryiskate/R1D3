/**
 * Test script for GDD HTML integration
 * This script verifies that our JavaScript files are loading properly
 * and the modals are functioning as expected
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('Test script loaded successfully');
    
    // Check if our required DOM elements exist
    const elementsToCheck = [
        { id: 'gdd-data', type: 'Data container' },
        { id: 'gdd-html-content', type: 'HTML content container' },
        { id: 'toc-container', type: 'TOC container' },
        { id: 'createTaskModal', type: 'Create task modal' },
        { id: 'linkTaskModal', type: 'Link task modal' },
        { id: 'task-section-id', type: 'Section ID input' },
        { id: 'section-title-display', type: 'Section title display' },
        { id: 'task-title', type: 'Task title input' },
        { id: 'link-task-form', type: 'Link task form' },
        { id: 'successToast', type: 'Success toast' }
    ];
    
    console.log('Checking for required DOM elements:');
    elementsToCheck.forEach(function(element) {
        const el = document.getElementById(element.id);
        console.log(`${element.type} (${element.id}): ${el ? 'Found' : 'NOT FOUND'}`);
    });
    
    // Check if our JavaScript variables are properly initialized
    console.log('Checking JavaScript variables:');
    try {
        const gddData = document.getElementById('gdd-data');
        if (gddData) {
            // Debug raw data attributes before parsing
            const rawSectionsData = gddData.getAttribute('data-sections');
            const rawSectionsWithTasksData = gddData.getAttribute('data-sections-with-tasks');
            
            console.log('Raw sections data:', rawSectionsData);
            console.log('Raw sections with tasks data:', rawSectionsWithTasksData);
            
            // Safely parse JSON with better error handling
            let sectionsJson = [];
            try {
                // Ensure we have valid JSON by checking for proper formatting
                if (rawSectionsData && 
                    (rawSectionsData.trim().startsWith('[') && rawSectionsData.trim().endsWith(']'))) {
                    sectionsJson = JSON.parse(rawSectionsData);
                } else {
                    console.warn('Sections data is not properly formatted JSON array, using empty array');
                    sectionsJson = [];
                }
            } catch (parseError) {
                console.error('Error parsing sections JSON:', parseError);
                console.log('Invalid JSON content:', rawSectionsData);
                // Provide a fallback
                sectionsJson = [];
            }
            
            let sectionsWithTasksJson = {};
            try {
                // Ensure we have valid JSON by checking for proper formatting
                if (rawSectionsWithTasksData && 
                    (rawSectionsWithTasksData.trim().startsWith('{') && rawSectionsWithTasksData.trim().endsWith('}'))) {
                    sectionsWithTasksJson = JSON.parse(rawSectionsWithTasksData);
                } else {
                    console.warn('Sections with tasks data is not properly formatted JSON object, using empty object');
                    sectionsWithTasksJson = {};
                }
            } catch (parseError) {
                console.error('Error parsing sections with tasks JSON:', parseError);
                console.log('Invalid JSON content:', rawSectionsWithTasksData);
                // Provide a fallback
                sectionsWithTasksJson = {};
            }
            
            console.log(`Sections JSON: ${sectionsJson.length} sections found`);
            console.log(`Sections with tasks JSON: ${Object.keys(sectionsWithTasksJson).length} sections with tasks found`);
            
            // Log first section for debugging
            if (sectionsJson.length > 0) {
                console.log('First section:', sectionsJson[0]);
            }
        } else {
            console.log('GDD data container not found');
        }
    } catch (error) {
        console.error('Error in GDD data processing:', error);
    }
    
    // Check if Bootstrap is properly loaded
    console.log('Checking Bootstrap:');
    if (typeof bootstrap !== 'undefined') {
        console.log('Bootstrap is loaded');
        console.log('Bootstrap version:', bootstrap.Tooltip.VERSION);
    } else {
        console.error('Bootstrap is NOT loaded');
    }
    
    // Check if jQuery is properly loaded
    console.log('Checking jQuery:');
    if (typeof jQuery !== 'undefined') {
        console.log('jQuery is loaded');
        console.log('jQuery version:', jQuery.fn.jquery);
    } else {
        console.error('jQuery is NOT loaded');
    }
    
    console.log('Test script completed');
});
