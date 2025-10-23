// Dashboard functionality
class Dashboard {
    constructor() {
        this.apiBase = window.API_BASE || 'http://localhost:8000';
        this.selectedUser = 'all'; // Track selected user
        this.init();
    }

    async init() {
        await this.loadDashboardData();
        this.setupEventListeners();
        this.startAutoRefresh();
    }

    setupEventListeners() {
        // Refresh button
        const refreshBtn = document.querySelector('[onclick="refreshDashboard()"]');
        if (refreshBtn) {
            refreshBtn.removeAttribute('onclick');
            refreshBtn.addEventListener('click', () => this.refreshDashboard());
        }
    }

    async loadDashboardData() {
        try {
            await Promise.all([
                this.loadSystemStats(),
                this.loadRecentActivity(),
                this.loadRecentAlerts(),
                this.loadSystemHealth()
            ]);
        } catch (error) {
            console.error('Error loading dashboard data:', error);
        }
    }

    async loadSystemStats() {
        try {
            // Load comprehensive analytics from new endpoint with user filter
            const url = this.selectedUser === 'all' 
                ? `${this.apiBase}/dashboard/analytics`
                : `${this.apiBase}/dashboard/analytics?user_id=${this.selectedUser}`;
                
            const response = await fetch(url);
            if (response.ok) {
                const data = await response.json();
                
                // Update all stat cards with real data
                this.updateStatCard('totalChats', data.total_conversations || 0);
                this.updateStatCard('avgResponseTime', `${data.avg_response_time || 0}ms`);
                this.updateStatCard('dailyCost', `$${data.daily_cost || 0}`);
                this.updateStatCard('activeAlerts', 0); // Will be updated by loadRecentAlerts
                
                // Update additional stats if elements exist
                this.updateStatCard('totalUsers', data.total_users || 0);
                this.updateStatCard('totalMessages', data.total_messages || 0);
                this.updateStatCard('activeSessions', data.active_sessions || 0);
                this.updateStatCard('totalDocuments', data.total_documents || 0);
                this.updateStatCard('systemUptime', this.formatUptime(data.system_uptime || 0));
                
                console.log(`Dashboard analytics loaded for ${this.selectedUser}:`, data);
            } else {
                console.error('Failed to load analytics:', response.status);
                // Fallback to showing zeros
                this.updateStatCard('totalChats', 0);
                this.updateStatCard('avgResponseTime', '0ms');
                this.updateStatCard('dailyCost', '$0.00');
            }
        } catch (error) {
            console.error('Error loading system stats:', error);
            // Show error state
            this.updateStatCard('totalChats', 'Error');
            this.updateStatCard('avgResponseTime', 'Error');
            this.updateStatCard('dailyCost', 'Error');
        }
    }

    changeSelectedUser(userId) {
        try {
            this.selectedUser = userId;
            console.log(`Switched to viewing data for: ${userId}`);
            this.loadDashboardData(); // Reload all data for selected user
        } catch (error) {
            console.error('Error changing selected user:', error);
            this.showToast('Error loading user data', 'error');
        }
    }

    showToast(message, type = 'info') {
        // Create toast notification
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${type === 'error' ? '#ef4444' : type === 'success' ? '#10b981' : '#3b82f6'};
            color: white;
            padding: 12px 20px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 10000;
            font-size: 14px;
            max-width: 300px;
            animation: slideInRight 0.3s ease;
        `;
        toast.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
            <span style="margin-left: 8px;">${message}</span>
        `;

        document.body.appendChild(toast);

        // Auto remove after 4 seconds
        setTimeout(() => {
            toast.style.animation = 'slideOutRight 0.3s ease forwards';
            setTimeout(() => {
                if (document.body.contains(toast)) {
                    document.body.removeChild(toast);
                }
            }, 300);
        }, 4000);
    }

    async loadRecentActivity() {
        const activityList = document.getElementById('recentActivity');
        if (!activityList) return;

        try {
            // Load real recent activity from new endpoint with user filter
            const url = this.selectedUser === 'all' 
                ? `${this.apiBase}/dashboard/recent-activity`
                : `${this.apiBase}/dashboard/recent-activity?user_id=${this.selectedUser}`;
                
            const response = await fetch(url);
            if (response.ok) {
                const data = await response.json();
                const activities = data.activities || [];
                
                if (activities.length > 0) {
                    activityList.innerHTML = activities.map(activity => `
                        <div class="activity-item">
                            <div class="activity-icon">
                                <i class="${activity.icon}"></i>
                            </div>
                            <div class="activity-content">
                                <p>${activity.text}</p>
                                <small>${activity.time}</small>
                            </div>
                        </div>
                    `).join('');
                } else {
                    activityList.innerHTML = `
                        <div class="activity-item">
                            <div class="activity-icon">
                                <i class="fas fa-info-circle"></i>
                            </div>
                            <div class="activity-content">
                                <p>No recent activity</p>
                                <small>Start a conversation to see activity</small>
                            </div>
                        </div>
                    `;
                }
            } else {
                throw new Error(`HTTP ${response.status}`);
            }
        } catch (error) {
            console.error('Error loading recent activity:', error);
            // Fallback to error message
            activityList.innerHTML = `
                <div class="activity-item">
                    <div class="activity-icon">
                        <i class="fas fa-exclamation-triangle text-warning"></i>
                    </div>
                    <div class="activity-content">
                        <p>Unable to load recent activity</p>
                        <small>Error: ${error.message}</small>
                    </div>
                </div>
            `;
        }
    }

    async loadRecentAlerts() {
        try {
            const response = await fetch(`${this.apiBase}/alerts/status`);
            if (response.ok) {
                const data = await response.json();
                this.updateStatCard('activeAlerts', data.active_alerts || 0);
                
                // Update alert badge
                const alertBadge = document.getElementById('alertBadge');
                if (alertBadge) {
                    alertBadge.textContent = data.active_alerts || 0;
                    alertBadge.style.display = data.active_alerts > 0 ? 'inline' : 'none';
                }
            }
        } catch (error) {
            console.error('Error loading alerts:', error);
        }
    }

    async loadSystemHealth() {
        try {
            // Load real system health from new endpoint
            const response = await fetch(`${this.apiBase}/dashboard/system-health`);
            if (response.ok) {
                const healthData = await response.json();
                
                // Update health status for each component
                Object.entries(healthData).forEach(([componentKey, componentData]) => {
                    const elementId = this.getHealthElementId(componentKey);
                    if (elementId) {
                        this.updateHealthStatus(elementId, componentData.status);
                    }
                });
                
                console.log('System health loaded:', healthData);
            } else {
                console.error('Failed to load system health:', response.status);
                // Set all to error state
                ['apiStatus', 'mlflowStatus', 'databaseStatus', 'vectorStoreStatus', 'emailAlertsStatus'].forEach(id => {
                    this.updateHealthStatus(id, 'error');
                });
            }
        } catch (error) {
            console.error('Error loading system health:', error);
            // Set all to error state
            ['apiStatus', 'mlflowStatus', 'databaseStatus', 'vectorStoreStatus', 'emailAlertsStatus'].forEach(id => {
                this.updateHealthStatus(id, 'error');
            });
        }
    }

    getHealthElementId(componentKey) {
        const mapping = {
            'api_server': 'apiStatus',
            'mlflow': 'mlflowStatus', 
            'database': 'databaseStatus',
            'vector_store': 'vectorStoreStatus',
            'email_alerts': 'emailAlertsStatus'
        };
        return mapping[componentKey];
    }

    formatUptime(seconds) {
        if (seconds < 60) {
            return `${Math.floor(seconds)}s`;
        } else if (seconds < 3600) {
            return `${Math.floor(seconds / 60)}m`;
        } else if (seconds < 86400) {
            return `${Math.floor(seconds / 3600)}h`;
        } else {
            return `${Math.floor(seconds / 86400)}d`;
        }
    }

    updateStatCard(id, value) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
            element.style.animation = 'pulse 0.3s ease-in-out';
        }
    }

    updateHealthStatus(id, status) {
        const element = document.getElementById(id);
        if (!element) return;

        const statusDot = element.querySelector('.status-dot');
        const statusText = element.querySelector('span:last-child');
        
        if (statusDot && statusText) {
            statusDot.className = `status-dot ${status}`;
            statusText.textContent = status === 'healthy' ? 'Healthy' : 'Error';
        }
    }

    async refreshDashboard() {
        const refreshBtn = document.querySelector('[onclick="refreshDashboard()"], .btn[data-action="refresh"]');
        if (refreshBtn) {
            refreshBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Refreshing...';
            refreshBtn.disabled = true;
        }

        await this.loadDashboardData();

        if (refreshBtn) {
            setTimeout(() => {
                refreshBtn.innerHTML = '<i class="fas fa-sync"></i> Refresh';
                refreshBtn.disabled = false;
            }, 1000);
        }
    }

    startAutoRefresh() {
        // Auto-refresh every 30 seconds
        setInterval(() => {
            this.loadDashboardData();
        }, 30000);
    }
}

// Global function for backward compatibility
function refreshDashboard() {
    if (window.dashboard) {
        window.dashboard.refreshDashboard();
    }
}

// Global functions for user selection
function filterUsers() {
    const input = document.getElementById('userSearchInput');
    const select = document.getElementById('userSelect');
    
    if (!input || !select) return;
    
    const filter = input.value.toLowerCase();
    const options = select.querySelectorAll('option');
    
    // Show all options first
    options.forEach(option => {
        option.style.display = 'block';
    });
    
    // If there's a filter, hide non-matching options
    if (filter.trim()) {
        options.forEach(option => {
            const text = option.textContent.toLowerCase();
            if (!text.includes(filter)) {
                option.style.display = 'none';
            }
        });
    }
}

function performSearch() {
    const input = document.getElementById('userSearchInput');
    const select = document.getElementById('userSelect');
    
    if (!input || !select) return;
    
    const searchTerm = input.value.toLowerCase().trim();
    const options = select.querySelectorAll('option');
    
    // Find exact match first
    let exactMatch = null;
    options.forEach(option => {
        if (option.textContent.toLowerCase() === searchTerm) {
            exactMatch = option;
        }
    });
    
    if (exactMatch) {
        select.value = exactMatch.value;
        changeSelectedUser();
        return;
    }
    
    // Find partial match
    let partialMatch = null;
    options.forEach(option => {
        if (option.textContent.toLowerCase().includes(searchTerm) && !partialMatch) {
            partialMatch = option;
        }
    });
    
    if (partialMatch) {
        select.value = partialMatch.value;
        changeSelectedUser();
    } else {
        // No match found, show error
        if (window.dashboard) {
            window.dashboard.showToast('No user found matching: ' + searchTerm, 'error');
        }
    }
}

function changeSelectedUser() {
    try {
        const userSelect = document.getElementById('userSelect');
        if (window.dashboard && userSelect) {
            window.dashboard.changeSelectedUser(userSelect.value);
        } else {
            console.error('Dashboard not initialized or user select element not found');
        }
    } catch (error) {
        console.error('Error in changeSelectedUser:', error);
        if (window.dashboard) {
            window.dashboard.showToast('Error changing user selection', 'error');
        }
    }
}

// Global functions for admin actions
function toggleUserMenu() {
    const dropdown = document.getElementById('userDropdown');
    if (dropdown) {
        dropdown.classList.toggle('show');
    }
}

// Close dropdown when clicking outside
document.addEventListener('click', function(event) {
    const userMenu = document.querySelector('.user-menu');
    const dropdown = document.getElementById('userDropdown');
    
    if (dropdown && !userMenu.contains(event.target)) {
        dropdown.classList.remove('show');
    }
});

function switchToUserView() {
    const session = localStorage.getItem('userSession');
    if (session) {
        try {
            const sessionData = JSON.parse(session);
            // Temporarily set role to 'user' for user view
            sessionData.role = 'user';
            sessionData.currentView = 'user';
            localStorage.setItem('userSession', JSON.stringify(sessionData));
            window.location.href = 'chat.html';
        } catch (error) {
            console.error('Error switching to user view:', error);
            window.location.href = 'login.html';
        }
    } else {
        window.location.href = 'login.html';
    }
}

function adminLogout() {
    try {
        // Clear session data
        localStorage.removeItem('userSession');
        sessionStorage.removeItem('isAuthenticated');
        
        // Show logout message and redirect
        if (window.dashboard) {
            window.dashboard.showToast('Admin logged out successfully', 'info');
        }
        
        setTimeout(() => {
            window.location.href = 'login.html';
        }, 500);
    } catch (error) {
        console.error('Error during logout:', error);
        // Force redirect even if there's an error
        window.location.href = 'login.html';
    }
}

// Global flags to prevent multiple initializations and redirect loops
window.dashboardInitialized = window.dashboardInitialized || false;
window.isRedirectingFromDashboard = window.isRedirectingFromDashboard || false;

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Prevent multiple initializations
    if (window.dashboardInitialized || window.dashboard) {
        console.log('Dashboard already initialized, skipping');
        return;
    }
    
    console.log('Initializing Dashboard...');
    window.dashboardInitialized = true;
    
    // Check admin authentication
    const session = localStorage.getItem('userSession');
    const isAuthenticated = sessionStorage.getItem('isAuthenticated');
    
    console.log('Dashboard auth check - Session exists:', !!session, 'Is authenticated:', isAuthenticated);
    
    if (!session) {
        console.log('No session found, redirecting to login');
        if (!window.isRedirectingFromDashboard && !window.isRedirectingToLogin) {
            window.isRedirectingFromDashboard = true;
            window.isRedirectingToLogin = true;
            setTimeout(() => {
                window.location.href = 'login.html';
            }, 100);
        }
        return;
    }
    
    try {
        const sessionData = JSON.parse(session);
        const now = new Date();
        const expiresAt = new Date(sessionData.expiresAt);
        
        console.log('Session data:', sessionData.username, 'Role:', sessionData.role);
        
        if (now >= expiresAt || sessionData.role !== 'admin') {
            console.log('Session expired or not admin, redirecting to login');
            localStorage.removeItem('userSession');
            sessionStorage.removeItem('isAuthenticated');
            if (!window.isRedirectingFromDashboard && !window.isRedirectingToLogin) {
                window.isRedirectingFromDashboard = true;
                window.isRedirectingToLogin = true;
                setTimeout(() => {
                    window.location.href = 'login.html';
                }, 100);
            }
            return;
        }
        
        // Ensure isAuthenticated is set for valid admin sessions
        sessionStorage.setItem('isAuthenticated', 'true');
        
        console.log('Dashboard authentication successful, initializing...');
        window.dashboard = new Dashboard();
        
    } catch (error) {
        console.error('Error parsing session:', error);
        localStorage.removeItem('userSession');
        sessionStorage.removeItem('isAuthenticated');
        if (!window.isRedirectingFromDashboard && !window.isRedirectingToLogin) {
            window.isRedirectingFromDashboard = true;
            window.isRedirectingToLogin = true;
            setTimeout(() => {
                window.location.href = 'login.html';
            }, 100);
        }
        return;
    }
});
