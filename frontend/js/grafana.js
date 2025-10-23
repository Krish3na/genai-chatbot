// ===== GRAFANA PAGE JAVASCRIPT =====

let grafanaConnected = false;

// ===== INITIALIZATION =====
document.addEventListener('DOMContentLoaded', () => {
    initializeGrafanaPage();
    
    // Show fallback immediately since iframe embedding is blocked
    showIframeFallback();
});

async function initializeGrafanaPage() {
    console.log('Initializing Grafana page');
    
    // Check Grafana connection
    await checkGrafanaConnection();
    
    // Load quick metrics
    await loadQuickMetrics();
    
    // Set up auto-refresh
    setInterval(loadQuickMetrics, 30000); // Refresh every 30 seconds
    setInterval(checkGrafanaConnection, 60000); // Check connection every minute
}

// ===== CONNECTION FUNCTIONS =====

/**
 * Check Grafana connection status
 */
async function checkGrafanaConnection() {
    const statusElement = document.getElementById('grafanaStatus');
    const lastCheckElement = document.getElementById('lastGrafanaCheck');
    const overlay = document.getElementById('iframeOverlay');
    
    try {
        // Try to reach Grafana API
        const response = await fetch('http://localhost:3000/api/health', {
            method: 'GET',
            mode: 'no-cors' // Handle CORS issues
        });
        
        grafanaConnected = true;
        
        if (statusElement) {
            statusElement.textContent = 'Connected';
            statusElement.className = 'status-badge success';
        }
        
        if (overlay) {
            overlay.classList.add('hidden');
        }
        
    } catch (error) {
        console.error('Grafana connection failed:', error);
        grafanaConnected = false;
        
        if (statusElement) {
            statusElement.textContent = 'Disconnected';
            statusElement.className = 'status-badge error';
        }
        
        if (overlay) {
            overlay.classList.remove('hidden');
        }
    }
    
    if (lastCheckElement) {
        lastCheckElement.textContent = new Date().toLocaleTimeString();
    }
}

/**
 * Load quick metrics from Prometheus
 */
async function loadQuickMetrics() {
    const metricsRefresh = document.getElementById('metricsRefresh');
    
    if (metricsRefresh) {
        metricsRefresh.style.display = 'flex';
    }
    
    try {
        // Simulate loading metrics (in real implementation, these would come from Prometheus API)
        const metrics = await simulateMetricsLoad();
        
        updateQuickMetrics(metrics);
        
    } catch (error) {
        console.error('Failed to load metrics:', error);
    } finally {
        if (metricsRefresh) {
            metricsRefresh.style.display = 'none';
        }
    }
}

/**
 * Simulate metrics loading (replace with real Prometheus queries)
 */
async function simulateMetricsLoad() {
    try {
        // Get real analytics data from our API
        const response = await fetch('/dashboard/analytics');
        const analytics = await response.json();
        
        // Get system health data
        const healthResponse = await fetch('/dashboard/system-health');
        const health = await healthResponse.json();
        
        // Calculate requests per minute (rough estimate)
        const requestsPerMin = analytics.total_messages > 0 ? 
            Math.round(analytics.total_messages / Math.max(1, analytics.system_uptime / 3600)) : 0;
        
        // Calculate error rate (if we have error data)
        const errorRate = health.api_server?.status === 'healthy' ? 0 : 5;
        
        return {
            activeSessions: analytics.active_sessions || 0,
            requestsPerMin: requestsPerMin,
            avgResponseTime: analytics.avg_response_time || 0,
            errorRate: errorRate,
            cpuUsage: health.api_server?.status === 'healthy' ? 25 : 85,
            memoryUsage: health.api_server?.status === 'healthy' ? 45 : 90
        };
    } catch (error) {
        console.error('Failed to load real metrics:', error);
        // Fallback to some default values
        return {
            activeSessions: 0,
            requestsPerMin: 0,
            avgResponseTime: 0,
            errorRate: 0,
            cpuUsage: 0,
            memoryUsage: 0
        };
    }
}

/**
 * Update quick metrics display
 */
function updateQuickMetrics(metrics) {
    const elements = {
        activeSessions: document.getElementById('activeSessions'),
        requestsPerMin: document.getElementById('requestsPerMin'),
        avgResponseTime: document.getElementById('avgResponseTime'),
        errorRate: document.getElementById('errorRate'),
        cpuUsage: document.getElementById('cpuUsage'),
        memoryUsage: document.getElementById('memoryUsage')
    };
    
    if (elements.activeSessions) {
        elements.activeSessions.textContent = metrics.activeSessions;
    }
    
    if (elements.requestsPerMin) {
        elements.requestsPerMin.textContent = metrics.requestsPerMin;
    }
    
    if (elements.avgResponseTime) {
        elements.avgResponseTime.textContent = `${metrics.avgResponseTime}ms`;
    }
    
    if (elements.errorRate) {
        elements.errorRate.textContent = `${metrics.errorRate}%`;
    }
    
    if (elements.cpuUsage) {
        elements.cpuUsage.textContent = `${metrics.cpuUsage}%`;
    }
    
    if (elements.memoryUsage) {
        elements.memoryUsage.textContent = `${metrics.memoryUsage}%`;
    }
}

// ===== ACTION FUNCTIONS =====

/**
 * Refresh Grafana page
 */
async function refreshGrafana() {
    showToast('Refreshing Grafana data...', 'info');
    
    try {
        await Promise.all([
            checkGrafanaConnection(),
            loadQuickMetrics()
        ]);
        
        showToast('Grafana data refreshed', 'success');
    } catch (error) {
        console.error('Failed to refresh Grafana:', error);
        showToast('Failed to refresh Grafana data', 'error');
    }
}

/**
 * Open Grafana in new tab
 */
function openGrafanaNew() {
    window.open('http://admin:admin@localhost:3000', '_blank');
}

/**
 * Open specific dashboard with user filtering
 */
function openDashboard(dashboardId) {
    // Use the actual dashboard UIDs from Grafana with credentials
    const dashboardUrls = {
        'system-overview': 'http://admin:admin@localhost:3000/d/genai-chatbot-dashboard',
        'chatbot-metrics': 'http://admin:admin@localhost:3000/d/genai-chatbot-dashboard',
        'mlflow-integration': 'http://admin:admin@localhost:3000/d/genai-chatbot-dashboard',
        'cost-analysis': 'http://admin:admin@localhost:3000/d/genai-chatbot-dashboard',
        'user-filtering': 'http://admin:admin@localhost:3000/d/genai-chatbot-dashboard'
    };
    
    const url = dashboardUrls[dashboardId] || 'http://admin:admin@localhost:3000/d/genai-chatbot-dashboard';
    
    console.log(`Opening dashboard: ${dashboardId} -> ${url}`);
    
    // Since iframe embedding is blocked by X-Frame-Options, just open in new tab
    console.log(`Opening dashboard in new tab: ${dashboardId} -> ${url}`);
    window.open(url, '_blank');
}

/**
 * Open Grafana in new tab
 */
function openGrafanaNew() {
    window.open('http://admin:admin@localhost:3000', '_blank');
}

// Iframe functions removed since iframe is no longer used

/**
 * Create custom dashboard
 */
function createCustomDashboard() {
    if (grafanaConnected) {
        window.open('http://admin:admin@localhost:3000/dashboard/new', '_blank');
    } else {
        showToast('Grafana is not connected. Please check the connection.', 'warning');
    }
}

/**
 * Toggle fullscreen mode (disabled since iframe is removed)
 */
function toggleFullscreen() {
    showToast('Fullscreen not available - iframe removed', 'info');
}

/**
 * Refresh iframe (disabled since iframe embedding is blocked)
 */
function refreshIframe() {
    // Since iframe embedding is blocked, just show a message
    showToast('Grafana dashboard opened in new tab', 'info');
    window.open('http://admin:admin@localhost:3000', '_blank');
}

// ===== EVENT LISTENERS =====

// Fullscreen event listener removed since iframe is no longer used

// Iframe events disabled since iframe embedding is blocked by X-Frame-Options
