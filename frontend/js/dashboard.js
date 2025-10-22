// Dashboard functionality
class Dashboard {
    constructor() {
        this.apiBase = window.API_BASE || 'http://localhost:8000';
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
            // Load chat statistics
            const response = await fetch(`${this.apiBase}/metrics`);
            if (response.ok) {
                const data = await response.json();
                this.updateStatCard('totalChats', data.total_requests || 0);
                this.updateStatCard('avgResponseTime', `${data.avg_response_time || 0}ms`);
                this.updateStatCard('dailyCost', `$${(data.daily_cost || 0).toFixed(2)}`);
            }
        } catch (error) {
            console.error('Error loading system stats:', error);
        }
    }

    async loadRecentActivity() {
        const activityList = document.getElementById('recentActivity');
        if (!activityList) return;

        try {
            // Mock recent activity data
            const activities = [
                { icon: 'fas fa-comment', text: 'New conversation started', time: '2 minutes ago' },
                { icon: 'fas fa-upload', text: 'Document uploaded for RAG', time: '5 minutes ago' },
                { icon: 'fas fa-chart-line', text: 'MLflow experiment logged', time: '10 minutes ago' },
                { icon: 'fas fa-bell', text: 'Alert threshold updated', time: '15 minutes ago' }
            ];

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
        } catch (error) {
            console.error('Error loading recent activity:', error);
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
        const healthChecks = [
            { id: 'apiStatus', endpoint: '/health', name: 'API Server' },
            { id: 'mlflowStatus', endpoint: 'http://localhost:5000', name: 'MLflow' }
        ];

        for (const check of healthChecks) {
            try {
                const response = await fetch(check.endpoint.startsWith('http') ? check.endpoint : `${this.apiBase}${check.endpoint}`);
                this.updateHealthStatus(check.id, response.ok ? 'healthy' : 'error');
            } catch (error) {
                this.updateHealthStatus(check.id, 'error');
            }
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
    // Clear session data
    localStorage.removeItem('userSession');
    sessionStorage.removeItem('isAuthenticated');
    
    // Show logout message and redirect
    if (window.dashboard) {
        window.dashboard.showToast('Admin logged out successfully', 'info');
    }
    
    setTimeout(() => {
        window.location.href = 'login.html';
    }, 1000);
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
    
    if (!session || !isAuthenticated) {
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
