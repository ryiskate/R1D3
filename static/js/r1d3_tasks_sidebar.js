/**
 * R1D3 Tasks Sidebar Management
 * This script ensures the R1D3 Tasks sidebar is displayed correctly
 */

document.addEventListener('DOMContentLoaded', function() {
    // Get the current path to determine if we're on an R1D3 Tasks page
    const currentPath = window.location.pathname;
    const sidebarContent = document.getElementById('sidebar-content');
    
    console.log('R1D3 Tasks sidebar script running, current path:', currentPath);
    
    // Only modify sidebar if we're on an R1D3 Tasks page or Epics page
    if (currentPath === '/R1D3-tasks/' || 
        currentPath.startsWith('/R1D3-tasks/') || 
        currentPath.startsWith('/projects/epics/') ||
        currentPath === '/' || 
        currentPath === '/dashboard/') {
        
        console.log('R1D3 Tasks path detected, updating sidebar');
        
        // Define the R1D3 Tasks sidebar HTML
        const r1d3SidebarHTML = `
            <div class="sidebar-heading">
                R1D3 Tasks
            </div>
            
            <li class="nav-item">
                <a class="nav-link ${currentPath.startsWith('/projects/epics/') ? 'active' : ''}" href="/projects/epics/">
                    <i class="fas fa-fw fa-layer-group"></i>
                    <span>Epics</span>
                </a>
            </li>
            
            <li class="nav-item">
                <a class="nav-link ${currentPath === '/R1D3-tasks/' ? 'active' : ''}" href="/R1D3-tasks/">
                    <i class="fas fa-fw fa-clipboard-list"></i>
                    <span>Task Dashboard</span>
                </a>
            </li>
            
            <li class="nav-item">
                <a class="nav-link ${currentPath === '/R1D3-tasks/newtask/' ? 'active' : ''}" href="/R1D3-tasks/newtask/">
                    <i class="fas fa-fw fa-plus-circle"></i>
                    <span>New R1D3 Task</span>
                </a>
            </li>
        `;
        
        // Update the sidebar content
        if (sidebarContent) {
            // Force override any existing content
            sidebarContent.innerHTML = r1d3SidebarHTML;
            console.log('R1D3 Tasks sidebar content updated successfully');
        } else {
            console.error('Sidebar content element not found for R1D3 Tasks');
        }
    }
});
