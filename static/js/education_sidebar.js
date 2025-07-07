/**
 * Education Department Sidebar
 * This script handles the sidebar content for the Education section
 * Created: 2025-07-07
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log("Education Sidebar Script loaded at " + new Date().toLocaleTimeString());
    
    // Only run this script for education section
    const currentPath = window.location.pathname;
    if (!currentPath.startsWith('/education')) {
        console.log('Not in education section, skipping education sidebar script');
        return;
    }
    
    // Get the sidebar content element
    const sidebarContent = document.getElementById('sidebar-content');
    if (!sidebarContent) {
        console.error('Sidebar content element not found');
        return;
    }
    
    // Define the education sidebar HTML
    const educationSidebarHTML = `
        <div class="sidebar-heading">
            Education Department
        </div>
        
        <li class="nav-item">
            <a class="nav-link ${currentPath === '/education/dashboard/' || currentPath === '/education/' ? 'active' : ''}" href="/education/dashboard/">
                <i class="fas fa-fw fa-chalkboard-teacher"></i>
                <span>Education Dashboard</span>
            </a>
        </li>
        
        <li class="nav-item">
            <a class="nav-link ${currentPath.includes('/education/courses') ? 'active' : ''}" href="/education/courses/">
                <i class="fas fa-fw fa-book"></i>
                <span>Courses</span>
            </a>
        </li>
        
        <li class="nav-item">
            <a class="nav-link ${currentPath.includes('/education/knowledge') ? 'active' : ''}" href="/education/knowledge/">
                <i class="fas fa-fw fa-lightbulb"></i>
                <span>Knowledge Base</span>
            </a>
        </li>
        
        <li class="nav-item">
            <a class="nav-link ${currentPath.includes('/education/tasks') ? 'active' : ''}" href="/education/tasks/">
                <i class="fas fa-fw fa-tasks"></i>
                <span>Education Tasks</span>
            </a>
        </li>
    `;
    
    // Set the sidebar content
    sidebarContent.innerHTML = educationSidebarHTML;
    console.log('Education sidebar content updated successfully');
});
