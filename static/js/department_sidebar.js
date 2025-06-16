/**
 * Department Sidebar Management
 * This script handles the dynamic loading of sidebar content based on the active department
 */

document.addEventListener('DOMContentLoaded', function() {
    // Get the current path to determine which department is active
    const currentPath = window.location.pathname;
    const sidebarContent = document.getElementById('sidebar-content');
    
    // Default sidebar content (Game Development)
    let sidebarHTML = `
        <div class="sidebar-heading">
            Game Development
        </div>
        
        <li class="nav-item">
            <a class="nav-link" href="/games/dashboard/">
                <i class="fas fa-fw fa-gamepad"></i>
                <span>Game Dashboard</span>
            </a>
        </li>
        
        <li class="nav-item">
            <a class="nav-link" href="/games/list/">
                <i class="fas fa-fw fa-list"></i>
                <span>Game Projects</span>
            </a>
        </li>
        
        <li class="nav-item">
            <a class="nav-link" href="/games/tasks/">
                <i class="fas fa-fw fa-tasks"></i>
                <span>Game Tasks</span>
            </a>
        </li>
    `;
    
    // Education Department
    if (currentPath.startsWith('/education')) {
        sidebarHTML = `
            <div class="sidebar-heading">
                Education
            </div>
            
            <li class="nav-item">
                <a class="nav-link" href="/education/dashboard/">
                    <i class="fas fa-fw fa-chalkboard-teacher"></i>
                    <span>Education Dashboard</span>
                </a>
            </li>
            
            <li class="nav-item">
                <a class="nav-link" href="/education/classes/">
                    <i class="fas fa-fw fa-graduation-cap"></i>
                    <span>Classes</span>
                </a>
            </li>
            
            <li class="nav-item">
                <a class="nav-link" href="/education/materials/">
                    <i class="fas fa-fw fa-book"></i>
                    <span>Course Materials</span>
                </a>
            </li>
            
            <li class="nav-item">
                <a class="nav-link" href="/education/schedule/">
                    <i class="fas fa-fw fa-calendar-alt"></i>
                    <span>Schedule</span>
                </a>
            </li>
            
            <li class="nav-item">
                <a class="nav-link" href="/education/tasks/">
                    <i class="fas fa-fw fa-tasks"></i>
                    <span>Education Tasks</span>
                </a>
            </li>
        `;
    }
    
    // Social Media Department
    else if (currentPath.startsWith('/social-media')) {
        sidebarHTML = `
            <div class="sidebar-heading">
                Social Media
            </div>
            
            <li class="nav-item">
                <a class="nav-link" href="/social-media/dashboard/">
                    <i class="fas fa-fw fa-users"></i>
                    <span>Social Dashboard</span>
                </a>
            </li>
            
            <li class="nav-item">
                <a class="nav-link" href="/social-media/schedule/">
                    <i class="fas fa-fw fa-calendar"></i>
                    <span>Post Schedule</span>
                </a>
            </li>
            
            <li class="nav-item">
                <a class="nav-link" href="/social-media/ideas/">
                    <i class="fas fa-fw fa-lightbulb"></i>
                    <span>Post Ideas</span>
                </a>
            </li>
            
            <li class="nav-item">
                <a class="nav-link" href="/social-media/analytics/">
                    <i class="fas fa-fw fa-chart-line"></i>
                    <span>Analytics</span>
                </a>
            </li>
            
            <li class="nav-item">
                <a class="nav-link" href="/social-media/tasks/">
                    <i class="fas fa-fw fa-tasks"></i>
                    <span>Social Media Tasks</span>
                </a>
            </li>
        `;
    }
    
    // Arcade Entertainment Department
    else if (currentPath.startsWith('/arcade')) {
        sidebarHTML = `
            <div class="sidebar-heading">
                Arcade Entertainment
            </div>
            
            <li class="nav-item">
                <a class="nav-link" href="/arcade/dashboard/">
                    <i class="fas fa-fw fa-arcade"></i>
                    <span>Arcade Dashboard</span>
                </a>
            </li>
            
            <li class="nav-item">
                <a class="nav-link" href="/arcade/projects/">
                    <i class="fas fa-fw fa-project-diagram"></i>
                    <span>Arcade Projects</span>
                </a>
            </li>
            
            <li class="nav-item">
                <a class="nav-link" href="/arcade/locations/">
                    <i class="fas fa-fw fa-map-marker-alt"></i>
                    <span>Locations</span>
                </a>
            </li>
            
            <li class="nav-item">
                <a class="nav-link" href="/arcade/revenue/">
                    <i class="fas fa-fw fa-coins"></i>
                    <span>Revenue</span>
                </a>
            </li>
            
            <li class="nav-item">
                <a class="nav-link" href="/arcade/tasks/">
                    <i class="fas fa-fw fa-tasks"></i>
                    <span>Arcade Tasks</span>
                </a>
            </li>
        `;
    }
    
    // Theme Park Department
    else if (currentPath.startsWith('/theme-park')) {
        sidebarHTML = `
            <div class="sidebar-heading">
                Theme Park
            </div>
            
            <li class="nav-item">
                <a class="nav-link" href="/theme-park/dashboard/">
                    <i class="fas fa-fw fa-mountain"></i>
                    <span>Park Dashboard</span>
                </a>
            </li>
            
            <li class="nav-item">
                <a class="nav-link" href="/theme-park/projects/">
                    <i class="fas fa-fw fa-project-diagram"></i>
                    <span>Park Projects</span>
                </a>
            </li>
            
            <li class="nav-item">
                <a class="nav-link" href="/theme-park/attractions/">
                    <i class="fas fa-fw fa-ticket-alt"></i>
                    <span>Attractions</span>
                </a>
            </li>
            
            <li class="nav-item">
                <a class="nav-link" href="/theme-park/map/">
                    <i class="fas fa-fw fa-map"></i>
                    <span>Park Map</span>
                </a>
            </li>
            
            <li class="nav-item">
                <a class="nav-link" href="/theme-park/tasks/">
                    <i class="fas fa-fw fa-tasks"></i>
                    <span>Theme Park Tasks</span>
                </a>
            </li>
        `;
    }
    
    // Update the sidebar content if the element exists
    if (sidebarContent) {
        sidebarContent.innerHTML = sidebarHTML;
    }
});
