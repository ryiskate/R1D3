/**
 * Custom sorting functions for R1D3 task tables
 * This file provides custom sorting functionality for DataTables
 */

// Wait for document to be ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('Task table sorting script loaded');
    
    // Add custom sorting for date columns
    if ($.fn.dataTable) {
        console.log('DataTables detected, adding custom sorting');
        
        // Custom date sorting function
        $.fn.dataTable.ext.type.order['date-custom-pre'] = function(data) {
            console.log('Sorting date:', data);
            
            // Handle empty cells or "No due date"
            if (!data || data.indexOf('No due date') !== -1) {
                return 9999999999; // Sort to the end
            }
            
            // Extract date from HTML content
            let dateText = '';
            
            // Try to extract from anchor tag first
            const anchor = $(data).find('a');
            if (anchor.length) {
                dateText = anchor.text().trim();
            } else {
                // Otherwise just get the text
                dateText = $(data).text().trim();
            }
            
            console.log('Extracted date text:', dateText);
            
            // Parse date in format "MMM d, YYYY" (e.g., "Jul 17, 2025")
            const monthMap = {
                'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
                'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08',
                'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'
            };
            
            const match = dateText.match(/(\w+)\s+(\d+),\s+(\d+)/);
            if (match) {
                const month = monthMap[match[1]] || '00';
                const day = match[2].padStart(2, '0');
                const year = match[3];
                
                const sortValue = parseInt(year + month + day);
                console.log('Parsed date for sorting:', year + month + day, '=', sortValue);
                return sortValue;
            }
            
            // If parsing fails, return original text for alphabetical sorting
            return dateText;
        };
        
        // Custom status sorting function
        $.fn.dataTable.ext.type.order['status-custom-pre'] = function(data) {
            console.log('Sorting status:', data);
            
            // Define status order (lower number = higher priority)
            const statusOrder = {
                'Blocked': 1,
                'To Do': 2,
                'In Progress': 3,
                'Review': 4,
                'Done': 5
            };
            
            // Extract status text from badge
            const statusText = $(data).text().trim();
            console.log('Extracted status:', statusText);
            
            // Return the order value or a high number if not found
            return statusOrder[statusText] || 999;
        };
        
        // Re-initialize the DataTable with custom sorting
        $(document).ready(function() {
            // Only proceed if the task table exists
            if ($('#taskTable').length) {
                console.log('Found task table, applying custom sorting');
                
                // If DataTable is already initialized, destroy it first
                if ($.fn.dataTable.isDataTable('#taskTable')) {
                    console.log('Destroying existing DataTable');
                    $('#taskTable').DataTable().destroy();
                }
                
                // Initialize DataTable with custom sorting
                const taskTable = $('#taskTable').DataTable({
                    "order": [[6, 'asc']], // Initial sort by due date
                    "columnDefs": [
                        // Checkbox column not sortable
                        { "orderable": false, "targets": 0 },
                        // Actions column not sortable
                        { "orderable": false, "targets": 7 },
                        // Status column with custom sorting
                        { 
                            "orderable": true, 
                            "targets": 3,
                            "type": 'status-custom'
                        },
                        // Due date column with custom sorting
                        { 
                            "orderable": true, 
                            "targets": 6,
                            "type": 'date-custom'
                        }
                    ],
                    "processing": true,
                    "serverSide": false,
                    "autoWidth": false,
                    "ordering": true,
                    "pageLength": 25,
                    "lengthMenu": [[10, 25, 50, -1], [10, 25, 50, "All"]],
                    "language": {
                        "emptyTable": "No tasks found",
                        "info": "Showing _START_ to _END_ of _TOTAL_ tasks",
                        "search": "Search tasks:"
                    },
                    "drawCallback": function(settings) {
                        // Re-attach event listeners
                        setTimeout(function() {
                            console.log('Re-attaching event listeners after DataTable draw');
                            if (typeof attachStatusDropdownListeners === 'function') {
                                attachStatusDropdownListeners();
                            }
                            if (typeof updateCheckboxListeners === 'function') {
                                updateCheckboxListeners();
                            }
                        }, 500);
                    }
                });
                
                console.log('DataTable initialization complete');
            }
        });
    } else {
        console.error('DataTables not found! Make sure jQuery and DataTables are loaded first.');
    }
});
