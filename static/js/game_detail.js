/**
 * Game Detail Page JavaScript
 * Handles progress bars and asset charts
 */

document.addEventListener('DOMContentLoaded', function() {
    // Set progress bar widths from task data
    setupProgressBars();
    
    // Initialize asset statistics chart
    setupAssetChart();
});

/**
 * Sets up the task progress bars with dynamic widths
 */
function setupProgressBars() {
    try {
        // Get task data from the JSON script element
        const taskDataElement = document.getElementById('task-data');
        if (!taskDataElement) return;
        
        const taskData = JSON.parse(taskDataElement.textContent);
        
        // Set widths for progress bars
        setProgressWidth('.progress-done', taskData.done);
        setProgressWidth('.progress-review', taskData.in_review);
        setProgressWidth('.progress-in-progress', taskData.in_progress);
        setProgressWidth('.progress-todo', taskData.to_do);
        setProgressWidth('.progress-blocked', taskData.blocked);
    } catch (error) {
        console.error('Error setting up progress bars:', error);
    }
}

/**
 * Helper function to set progress bar width with fallback
 */
function setProgressWidth(selector, value) {
    const element = document.querySelector(selector);
    if (element) {
        const width = (value || 0) + '%';
        element.style.width = width;
        element.setAttribute('aria-valuenow', value || 0);
        
        // Add percentage text if width is sufficient
        if ((value || 0) > 5) {
            element.textContent = width;
        }
    }
}

/**
 * Sets up the asset statistics doughnut chart
 */
function setupAssetChart() {
    try {
        // Get asset data from the JSON script element
        const assetDataElement = document.getElementById('asset-data');
        if (!assetDataElement) return;
        
        const assetData = JSON.parse(assetDataElement.textContent);
        
        // Get chart canvas context
        const ctx = document.getElementById('assetChart');
        if (!ctx) return;
        
        // Create chart
        new Chart(ctx.getContext('2d'), {
            type: 'doughnut',
            data: {
                labels: ['3D Models', '2D Images', 'Music', 'Videos', 'References', 'Other'],
                datasets: [{
                    data: [
                        assetData['3d_model'] || 0,
                        assetData['2d_image'] || 0,
                        assetData.music || 0,
                        assetData.video || 0,
                        assetData.reference || 0,
                        assetData.other || 0
                    ],
                    backgroundColor: [
                        '#4e73df', '#1cc88a', '#36b9cc', '#f6c23e', '#e74a3b', '#858796'
                    ]
                }]
            },
            options: {
                maintainAspectRatio: false,
                legend: {
                    display: false
                },
                cutoutPercentage: 70
            }
        });
    } catch (error) {
        console.error('Error setting up asset chart:', error);
    }
}
