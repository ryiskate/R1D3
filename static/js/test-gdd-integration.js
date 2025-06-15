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
            const sectionsJson = JSON.parse(gddData.getAttribute('data-sections') || '[]');
            const sectionsWithTasksJson = JSON.parse(gddData.getAttribute('data-sections-with-tasks') || '{}');
            
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
        console.error('Error parsing JSON data:', error);
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
