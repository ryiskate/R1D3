/**
 * Debug Sidebar Script
 * This script helps identify issues with the sidebar navigation
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log("Debug Sidebar Script loaded at " + new Date().toLocaleTimeString());
    
    // Find all Game Dashboard links
    const gameDashboardLinks = document.querySelectorAll('a[href*="games:dashboard"], a[href*="/games/dashboard/"], a[href="/games/"], a[href="/games"]');
    
    console.log("Found " + gameDashboardLinks.length + " Game Dashboard links");
    
    // Log details about each link
    gameDashboardLinks.forEach((link, index) => {
        console.log(`Link ${index + 1}:`, {
            href: link.href,
            innerHTML: link.innerHTML,
            outerHTML: link.outerHTML,
            parentElement: link.parentElement.tagName
        });
        
        // Fix the URL to point to /games/
        if (link.href.includes('/games/dashboard/')) {
            console.log(`Fixing link ${index + 1} from ${link.href} to /games/`);
            link.href = '/games/';
            
            // Add a visual indicator
            const span = link.querySelector('span');
            if (span) {
                span.innerHTML = '<span class="badge bg-danger rounded-pill me-1">FIXED</span> Game Dashboard';
            }
        }
    });
    
    // Monitor for changes to the sidebar
    const sidebarContent = document.getElementById('sidebar-content');
    if (sidebarContent) {
        console.log("Found sidebar-content element");
        
        // Create a MutationObserver to watch for changes to the sidebar
        const observer = new MutationObserver((mutations) => {
            console.log("Sidebar content changed at " + new Date().toLocaleTimeString());
            
            // Check for Game Dashboard links again after the change
            const updatedLinks = document.querySelectorAll('a[href*="games:dashboard"], a[href*="/games/dashboard/"], a[href="/games/"], a[href="/games"]');
            
            console.log("Found " + updatedLinks.length + " Game Dashboard links after sidebar update");
            
            // Fix any incorrect links
            updatedLinks.forEach((link, index) => {
                console.log(`Updated Link ${index + 1}:`, {
                    href: link.href,
                    innerHTML: link.innerHTML,
                    outerHTML: link.outerHTML
                });
                
                // Fix the URL to point to /games/
                if (link.href.includes('/games/dashboard/')) {
                    console.log(`Fixing updated link ${index + 1} from ${link.href} to /games/`);
                    link.href = '/games/';
                    
                    // Add a visual indicator
                    const span = link.querySelector('span');
                    if (span) {
                        span.innerHTML = '<span class="badge bg-danger rounded-pill me-1">FIXED</span> Game Dashboard';
                    }
                }
            });
        });
        
        // Start observing the sidebar content
        observer.observe(sidebarContent, { childList: true, subtree: true });
    }
});
