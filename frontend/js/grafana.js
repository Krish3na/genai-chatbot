// ===== GRAFANA PAGE JAVASCRIPT =====

let grafanaConnected = false;

// ===== INITIALIZATION =====
document.addEventListener('DOMContentLoaded', () => {
    initializeGrafanaPage();
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
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    return {
        activeSessions: Math.floor(Math.random() * 50) + 10,
        requestsPerMin: Math.floor(Math.random() * 100) + 20,
        avgResponseTime: (Math.random() * 2 + 1).toFixed(1) * 1000,
        errorRate: (Math.random() * 5).toFixed(1),
        cpuUsage: Math.floor(Math.random() * 60) + 20,
        memoryUsage: Math.floor(Math.random() * 40) + 30
    };
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
    GenAI.showToast('Refreshing Grafana data...', 'info');
    
    try {
        await Promise.all([
            checkGrafanaConnection(),
            loadQuickMetrics()
        ]);
        
        GenAI.showToast('Grafana data refreshed', 'success');
    } catch (error) {
        console.error('Failed to refresh Grafana:', error);
        GenAI.showToast('Failed to refresh Grafana data', 'error');
    }
}

/**
 * Open Grafana in new tab
 */
function openGrafanaNew() {
    window.open('http://localhost:3000', '_blank');
}

/**
 * Open specific dashboard
 */
function openDashboard(dashboardId) {
    const dashboardUrls = {
        'system-overview': 'http://localhost:3000/d/system-overview',
        'chatbot-metrics': 'http://localhost:3000/d/chatbot-metrics',
        'mlflow-integration': 'http://localhost:3000/d/mlflow-integration',
        'cost-analysis': 'http://localhost:3000/d/cost-analysis'
    };
    
    const url = dashboardUrls[dashboardId] || 'http://localhost:3000';
    
    if (grafanaConnected) {
        // Update embedded iframe
        const iframe = document.getElementById('grafanaIframe');
        if (iframe) {
            iframe.src = url;
        }
    } else {
        // Open in new tab if not connected
        window.open(url, '_blank');
    }
}

/**
 * Create custom dashboard
 */
function createCustomDashboard() {
    if (grafanaConnected) {
        window.open('http://localhost:3000/dashboard/new', '_blank');
    } else {
        GenAI.showToast('Grafana is not connected. Please check the connection.', 'warning');
    }
}

/**
 * Toggle fullscreen mode
 */
function toggleFullscreen() {
    const container = document.getElementById('grafanaContainer');
    const iframe = document.getElementById('grafanaIframe');
    
    if (!container || !iframe) return;
    
    if (!document.fullscreenElement) {
        container.requestFullscreen().then(() => {
            iframe.style.height = '100vh';
        }).catch(err => {
            console.error('Error attempting to enable fullscreen:', err);
            GenAI.showToast('Fullscreen not supported', 'warning');
        });
    } else {
        document.exitFullscreen().then(() => {
            iframe.style.height = '600px';
        });
    }
}

/**
 * Refresh iframe
 */
function refreshIframe() {
    const iframe = document.getElementById('grafanaIframe');
    if (iframe) {
        iframe.src = iframe.src;
        GenAI.showToast('Grafana dashboard refreshed', 'info');
    }
}

// ===== EVENT LISTENERS =====

// Handle fullscreen changes
document.addEventListener('fullscreenchange', () => {
    const iframe = document.getElementById('grafanaIframe');
    if (iframe) {
        if (document.fullscreenElement) {
            iframe.style.height = '100vh';
        } else {
            iframe.style.height = '600px';
        }
    }
});

// Handle iframe load events
document.addEventListener('DOMContentLoaded', () => {
    const iframe = document.getElementById('grafanaIframe');
    if (iframe) {
        iframe.addEventListener('load', () => {
            console.log('Grafana iframe loaded successfully');
        });
        
        iframe.addEventListener('error', () => {
            console.error('Grafana iframe failed to load');
            const overlay = document.getElementById('iframeOverlay');
            if (overlay) {
                overlay.classList.remove('hidden');
            }
        });
    }
});
