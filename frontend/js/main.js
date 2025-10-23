// ===== MAIN APPLICATION JAVASCRIPT =====

// Configuration
const CONFIG = {
    API_BASE_URL: 'http://localhost:8000',
    REFRESH_INTERVAL: 30000, // 30 seconds
    MAX_RETRIES: 3,
    RETRY_DELAY: 1000 // 1 second
};

// Global state
let currentUser = 'Admin';
let systemHealth = {
    api: 'healthy',
    mlflow: 'healthy', 
    database: 'healthy',
    email: 'not-configured'
};

// ===== UTILITY FUNCTIONS =====

/**
 * Make API request with retry logic
 */
async function apiRequest(endpoint, options = {}) {
    const url = `${CONFIG.API_BASE_URL}${endpoint}`;
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
        },
        ...options
    };

    for (let attempt = 1; attempt <= CONFIG.MAX_RETRIES; attempt++) {
        try {
            const response = await fetch(url, defaultOptions);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error(`API request attempt ${attempt} failed:`, error);
            
            if (attempt === CONFIG.MAX_RETRIES) {
                throw error;
            }
            
            // Wait before retrying
            await new Promise(resolve => setTimeout(resolve, CONFIG.RETRY_DELAY * attempt));
        }
    }
}

/**
 * Format timestamp to readable string
 */
function formatTimestamp(timestamp) {
    const date = new Date(timestamp * 1000);
    return date.toLocaleString();
}

/**
 * Format duration in milliseconds to readable string
 */
function formatDuration(ms) {
    if (ms < 1000) {
        return `${Math.round(ms)}ms`;
    } else if (ms < 60000) {
        return `${(ms / 1000).toFixed(1)}s`;
    } else {
        return `${(ms / 60000).toFixed(1)}m`;
    }
}

/**
 * Format cost to currency string
 */
function formatCost(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 2,
        maximumFractionDigits: 4
    }).format(amount);
}

/**
 * Show toast notification
 */
function showToast(message, type = 'info') {
    // Remove existing toasts
    const existingToasts = document.querySelectorAll('.toast');
    existingToasts.forEach(toast => toast.remove());

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <div class="toast-content">
            <i class="fas fa-${getToastIcon(type)}"></i>
            <span>${message}</span>
        </div>
        <button class="toast-close" onclick="this.parentElement.remove()">
            <i class="fas fa-times"></i>
        </button>
    `;

    document.body.appendChild(toast);

    // Auto remove after 5 seconds
    setTimeout(() => {
        if (toast.parentElement) {
            toast.remove();
        }
    }, 5000);
}

function getToastIcon(type) {
    const icons = {
        success: 'check-circle',
        error: 'exclamation-circle',
        warning: 'exclamation-triangle',
        info: 'info-circle'
    };
    return icons[type] || 'info-circle';
}

/**
 * Update system status indicator
 */
function updateSystemStatus(status = 'healthy') {
    const statusDots = document.querySelectorAll('#systemStatus');
    statusDots.forEach(dot => {
        dot.className = `status-dot ${status}`;
    });
}

/**
 * Update alert badge in navigation
 */
function updateAlertBadge(count) {
    const badges = document.querySelectorAll('#alertBadge');
    badges.forEach(badge => {
        badge.textContent = count;
        badge.style.display = count > 0 ? 'inline-block' : 'none';
    });
}

// ===== NAVIGATION FUNCTIONS =====

/**
 * Initialize sidebar toggle functionality
 */
function initializeSidebar() {
    // Handle admin sidebar
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');

    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', () => {
            sidebar.classList.toggle('active');
        });

        // Close sidebar when clicking outside on mobile
        document.addEventListener('click', (e) => {
            if (window.innerWidth <= 768 && 
                !sidebar.contains(e.target) && 
                !sidebarToggle.contains(e.target)) {
                sidebar.classList.remove('active');
            }
        });
    }

    // Handle user sidebar
    const userSidebarToggle = document.getElementById('userSidebarToggle');
    const userSidebar = document.getElementById('userSidebar');

    if (userSidebarToggle && userSidebar) {
        userSidebarToggle.addEventListener('click', () => {
            userSidebar.classList.toggle('active');
        });

        // Close sidebar when clicking outside on mobile
        document.addEventListener('click', (e) => {
            if (window.innerWidth <= 768 && 
                !userSidebar.contains(e.target) && 
                !userSidebarToggle.contains(e.target)) {
                userSidebar.classList.remove('active');
            }
        });
    }
}

// ===== SYSTEM HEALTH FUNCTIONS =====

/**
 * Check system health status
 */
async function checkSystemHealth() {
    try {
        // Check API health
        const healthResponse = await apiRequest('/health');
        systemHealth.api = healthResponse.status === 'healthy' ? 'healthy' : 'warning';

        // Check MLflow status (if available)
        try {
            await apiRequest('/mlflow/experiments');
            systemHealth.mlflow = 'healthy';
        } catch {
            systemHealth.mlflow = 'warning';
        }

        // Check alert system status (if available)
        try {
            const alertStatus = await apiRequest('/alerts/status');
            systemHealth.email = alertStatus.email_configured ? 'healthy' : 'warning';
        } catch {
            systemHealth.email = 'not-configured';
        }

        // Update UI
        updateSystemHealthUI();
        
        // Determine overall status
        const hasWarnings = Object.values(systemHealth).some(status => 
            status === 'warning' || status === 'not-configured'
        );
        const hasErrors = Object.values(systemHealth).some(status => status === 'error');
        
        const overallStatus = hasErrors ? 'danger' : hasWarnings ? 'warning' : 'healthy';
        updateSystemStatus(overallStatus);

    } catch (error) {
        console.error('System health check failed:', error);
        systemHealth.api = 'error';
        updateSystemStatus('danger');
        updateSystemHealthUI();
    }
}

/**
 * Update system health UI elements
 */
function updateSystemHealthUI() {
    const healthElements = {
        apiStatus: systemHealth.api,
        mlflowStatus: systemHealth.mlflow,
        dbStatus: systemHealth.database,
        emailStatus: systemHealth.email
    };

    Object.entries(healthElements).forEach(([elementId, status]) => {
        const element = document.getElementById(elementId);
        if (element) {
            const dot = element.querySelector('.status-dot');
            const text = element.querySelector('span:last-child');
            
            if (dot) {
                dot.className = `status-dot ${status}`;
            }
            
            if (text) {
                text.textContent = getStatusText(status);
            }
        }
    });
}

function getStatusText(status) {
    const statusTexts = {
        healthy: 'Healthy',
        warning: 'Warning',
        error: 'Error',
        'not-configured': 'Not Configured'
    };
    return statusTexts[status] || 'Unknown';
}

// ===== ALERT FUNCTIONS =====

/**
 * Check for active alerts
 */
async function checkActiveAlerts() {
    try {
        const alertsResponse = await apiRequest('/alerts/check');
        const totalAlerts = alertsResponse.total_alerts || 0;
        
        updateAlertBadge(totalAlerts);
        
        return alertsResponse;
    } catch (error) {
        console.error('Failed to check alerts:', error);
        updateAlertBadge(0);
        return null;
    }
}

// ===== INITIALIZATION =====

/**
 * Initialize the application
 */
document.addEventListener('DOMContentLoaded', () => {
    console.log('GenAI Chatbot Frontend initialized');
    
    // Initialize components
    initializeSidebar();
    
    // Initial system checks
    checkSystemHealth();
    checkActiveAlerts();
    
    // Set up periodic updates
    setInterval(() => {
        checkSystemHealth();
        checkActiveAlerts();
    }, CONFIG.REFRESH_INTERVAL);
    
    // Add global error handler
    window.addEventListener('error', (e) => {
        console.error('Global error:', e.error);
        showToast('An unexpected error occurred', 'error');
    });
    
    // Add unhandled promise rejection handler
    window.addEventListener('unhandledrejection', (e) => {
        console.error('Unhandled promise rejection:', e.reason);
        showToast('A network error occurred', 'error');
    });
});

// ===== GLOBAL FUNCTIONS =====

/**
 * Refresh dashboard data
 */
async function refreshDashboard() {
    showToast('Refreshing dashboard...', 'info');
    
    try {
        await Promise.all([
            checkSystemHealth(),
            checkActiveAlerts()
        ]);
        
        showToast('Dashboard refreshed successfully', 'success');
    } catch (error) {
        console.error('Dashboard refresh failed:', error);
        showToast('Failed to refresh dashboard', 'error');
    }
}

/**
 * Open MLflow UI in new tab
 */
function openMLflow() {
    window.open('http://localhost:5000', '_blank');
}

// Export functions for use in other scripts
window.GenAI = {
    apiRequest,
    formatTimestamp,
    formatDuration,
    formatCost,
    showToast,
    updateSystemStatus,
    updateAlertBadge,
    checkSystemHealth,
    checkActiveAlerts,
    refreshDashboard,
    openMLflow,
    CONFIG
};
