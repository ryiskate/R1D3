/**
 * Debug script to verify JavaScript execution on the task dashboard
 */
console.log('%c DEBUG TASK DASHBOARD SCRIPT LOADED', 'background: #ff0000; color: white; padding: 10px; font-size: 16px; font-weight: bold;');

// Check if the document is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('%c Document is ready!', 'background: #00ff00; color: black; padding: 5px;');
    
    // Check if jQuery is available
    if (typeof $ !== 'undefined') {
        console.log('jQuery version:', $.fn.jquery);
    } else {
        console.error('jQuery is not available!');
    }
    
    // Check if DataTables is available
    if (typeof $.fn.DataTable !== 'undefined') {
        console.log('DataTables is available');
    } else {
        console.error('DataTables is not available!');
    }
    
    // Check if the task table exists
    const taskTable = document.getElementById('taskTable');
    if (taskTable) {
        console.log('Task table found:', taskTable);
        console.log('Task table columns:', taskTable.querySelectorAll('th').length);
    } else {
        console.error('Task table not found!');
    }
    
    // Check if status options exist
    const statusOptions = document.querySelectorAll('.status-option');
    console.log('Status options found:', statusOptions.length);
    
    // Try to initialize a simple DataTable
    try {
        if (typeof $ !== 'undefined' && typeof $.fn.DataTable !== 'undefined' && $('#taskTable').length > 0) {
            console.log('Attempting to initialize a simple DataTable...');
            const simpleTable = $('#taskTable').DataTable({
                "paging": false,
                "ordering": true,
                "info": false,
                "searching": false
            });
            console.log('Simple DataTable initialized successfully');
        }
    } catch (error) {
        console.error('Error initializing DataTable:', error);
    }
});
