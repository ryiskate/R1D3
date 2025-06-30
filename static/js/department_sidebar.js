/**
 * Department Sidebar Management (Version 2)
 * This script handles the dynamic loading of sidebar content based on the active department
 * Updated: 2025-06-26
 */

document.addEventListener('DOMContentLoaded', function() {
    // Get the current path to determine which department is active
    const currentPath = window.location.pathname;
    const sidebarContent = document.getElementById('sidebar-content');
    
    console.log('Current path:', currentPath);
    
    // Don't modify the sidebar if we're on a debug page or indie news section
    if (currentPath.includes('/debug-') || currentPath.includes('/indie-news') || currentPath.includes('/indie_news')) {
        console.log('Skipping sidebar modification for special section');
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
                <a class="nav-link" href="/education/courses/">
                    <i class="fas fa-fw fa-book"></i>
                    <span>Courses</span>
                </a>
            </li>
            
            <li class="nav-item">
                <a class="nav-link ${currentPath === '/education/tasks/' ? 'active' : ''}" href="/education/tasks/">
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
                    <i class="fas fa-fw fa-mountain"></i>
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
                <a class="nav-link" href="/theme-park/tasks/">
                    <i class="fas fa-fw fa-tasks"></i>
                    <span>Theme Park Tasks</span>
                </a>
            </li>
            
            <li class="nav-item">
                <a class="nav-link" href="/theme-park/maintenance/">
                    <i class="fas fa-fw fa-tools"></i>
                    <span>Maintenance</span>
                </a>
            </li>
        `;
    }
    
    // Indie News Department
    if (currentPath.includes('/indie-news') || currentPath.includes('/indie_news')) {
        sidebarHTML = `
            <div class="sidebar-heading">
                Indie News
            </div>
            
            <li class="nav-item">
                <a class="nav-link ${currentPath === '/indie-news/' || currentPath === '/indie-news' ? 'active' : ''}" href="/indie-news/">
                    <i class="fas fa-fw fa-newspaper"></i>
                    <span>News Dashboard</span>
                </a>
            </li>
            
            <li class="nav-item">
                <a class="nav-link ${currentPath === '/indie-news/tasks/' ? 'active' : ''}" href="/indie-news/tasks/">
                    <i class="fas fa-fw fa-tasks"></i>
                    <span>News Tasks</span>
                </a>
            </li>
            
            <li class="nav-item">
                <a class="nav-link ${currentPath === '/indie-news/games/' ? 'active' : ''}" href="/indie-news/games/">
                    <i class="fas fa-fw fa-gamepad"></i>
                    <span>Indie Games</span>
                </a>
            </li>
            
            <li class="nav-item">
                <a class="nav-link ${currentPath === '/indie-news/events/' ? 'active' : ''}" href="/indie-news/events/">
                    <i class="fas fa-fw fa-calendar-alt"></i>
                    <span>Events</span>
                </a>
            </li>
            
            <li class="nav-item">
                <a class="nav-link ${currentPath === '/indie-news/tools/' ? 'active' : ''}" href="/indie-news/tools/">
                    <i class="fas fa-fw fa-tools"></i>
                    <span>Dev Tools</span>
                </a>
            </li>
        `;
    }
    
    // Update the sidebar content
    console.log('Setting sidebar HTML for path:', currentPath);
    console.log('Sidebar content element exists:', !!sidebarContent);
    
    if (sidebarContent) {
        sidebarContent.innerHTML = sidebarHTML;
        console.log('Sidebar content updated');
    } else {
        console.error('Sidebar content element not found');
    }
    console.log("Sidebar updated with version 2 script at " + new Date().toLocaleTimeString());
});
