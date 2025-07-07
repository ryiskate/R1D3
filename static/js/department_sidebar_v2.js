/**
 * Department Sidebar Management (Version 2)
 * This script handles the dynamic loading of sidebar content based on the active department
 * Updated: 2025-06-26
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log("Department Sidebar V2 Script loaded at " + new Date().toLocaleTimeString());
    
    // Get the current path
    const currentPath = window.location.pathname;
    
    // Get the sidebar content element
    const sidebarContent = document.getElementById('sidebar-content');
    
    // Don't modify the sidebar if we're on a debug page or in the education section
    if (currentPath.includes('/debug/') || currentPath.startsWith('/education')) {
        console.log('Debug page or education section detected, skipping sidebar modification');
        return;
    }
    
    // Check if we're on the game dashboard page
    const isGameDashboard = currentPath === '/games/' || currentPath === '/games';
    
    // Default sidebar content (Game Development)
    let sidebarHTML = `
        <div class="sidebar-heading">
            Game Development
        </div>
        
        <li class="nav-item">
            <a class="nav-link ${isGameDashboard ? 'active' : ''}" href="/games/">
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
    }
    
    // Social Media Department
    if (currentPath.startsWith('/social-media')) {
        sidebarHTML = `
            <div class="sidebar-heading">
                Social Media
            </div>
            
            <li class="nav-item">
                <a class="nav-link" href="/social-media/dashboard/">
                    <i class="fas fa-fw fa-hashtag"></i>
                    <span>Social Media Dashboard</span>
                </a>
            </li>
            
            <li class="nav-item">
                <a class="nav-link" href="/social-media/campaigns/">
                    <i class="fas fa-fw fa-bullhorn"></i>
                    <span>Campaigns</span>
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
    
    // Arcade Department
    if (currentPath.startsWith('/arcade')) {
        sidebarHTML = `
            <div class="sidebar-heading">
                Arcade
            </div>
            
            <li class="nav-item">
                <a class="nav-link" href="/arcade/dashboard/">
                    <i class="fas fa-fw fa-joystick"></i>
                    <span>Arcade Dashboard</span>
                </a>
            </li>
            
            <li class="nav-item">
                <a class="nav-link" href="/arcade/machines/">
                    <i class="fas fa-fw fa-arcade-machine"></i>
                    <span>Machines</span>
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
    if (currentPath.startsWith('/theme-park')) {
        sidebarHTML = `
            <div class="sidebar-heading">
                Theme Park
            </div>
            
            <li class="nav-item">
                <a class="nav-link" href="/theme-park/dashboard/">
                    <i class="fas fa-fw fa-ferris-wheel"></i>
                    <span>Theme Park Dashboard</span>
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
        console.log("Sidebar updated with version 2 script at " + new Date().toLocaleTimeString());
    }
});
