// ===== PROMETHEUS PAGE JAVASCRIPT =====

let prometheusConnected = false;
let currentTimeRange = '1h';

// ===== INITIALIZATION =====
document.addEventListener('DOMContentLoaded', () => {
    initializePrometheusPage();
});

async function initializePrometheusPage() {
    console.log('Initializing Prometheus page');
    
    // Check Prometheus connection
    await checkPrometheusConnection();
    
    // Load available metrics
    await loadAvailableMetrics();
    
    // Load key metrics
    await loadKeyMetrics();
    
    // Set up auto-refresh
    setInterval(loadKeyMetrics, 30000); // Refresh every 30 seconds
    setInterval(checkPrometheusConnection, 60000); // Check connection every minute
}

// ===== CONNECTION FUNCTIONS =====

/**
 * Check Prometheus connection status
 */
async function checkPrometheusConnection() {
    const statusElement = document.getElementById('prometheusStatus');
    const targetsElement = document.getElementById('prometheusTargets');
    const lastScrapeElement = document.getElementById('lastScrape');
    const overlay = document.getElementById('prometheusOverlay');
    
    try {
        // Try to reach Prometheus API
        const response = await fetch('http://localhost:9090/api/v1/query?query=up', {
            method: 'GET',
            mode: 'no-cors' // Handle CORS issues
        });
        
        prometheusConnected = true;
        
        if (statusElement) {
            statusElement.textContent = 'Connected';
            statusElement.className = 'status-badge success';
        }
        
        if (overlay) {
            overlay.classList.add('hidden');
        }
        
        // Simulate targets count
        if (targetsElement) {
            targetsElement.textContent = '3 targets';
        }
        
    } catch (error) {
        console.error('Prometheus connection failed:', error);
        prometheusConnected = false;
        
        if (statusElement) {
            statusElement.textContent = 'Disconnected';
            statusElement.className = 'status-badge error';
        }
        
        if (overlay) {
            overlay.classList.remove('hidden');
        }
        
        if (targetsElement) {
            targetsElement.textContent = 'Unknown';
        }
    }
    
    if (lastScrapeElement) {
        lastScrapeElement.textContent = new Date().toLocaleTimeString();
    }
}

/**
 * Load available metrics from Prometheus
 */
async function loadAvailableMetrics() {
    const metricsList = document.getElementById('metricsList');
    if (!metricsList) return;
    
    try {
        // Simulate metrics list (in real implementation, use /api/v1/label/__name__/values)
        const metrics = [
            { name: 'up', description: 'Whether the instance is up' },
            { name: 'http_requests_total', description: 'Total number of HTTP requests' },
            { name: 'http_request_duration_seconds', description: 'HTTP request duration in seconds' },
            { name: 'chat_response_time_seconds', description: 'Chat response time in seconds' },
            { name: 'chat_requests_total', description: 'Total number of chat requests' },
            { name: 'openai_api_calls_total', description: 'Total OpenAI API calls' },
            { name: 'openai_api_cost_total', description: 'Total OpenAI API cost' },
            { name: 'mlflow_experiments_total', description: 'Total MLflow experiments' },
            { name: 'system_cpu_usage_percent', description: 'System CPU usage percentage' },
            { name: 'system_memory_usage_bytes', description: 'System memory usage in bytes' },
            { name: 'prometheus_tsdb_head_samples_appended_total', description: 'Prometheus samples appended' },
            { name: 'prometheus_config_last_reload_successful', description: 'Prometheus config reload status' }
        ];
        
        metricsList.innerHTML = metrics.map(metric => `
            <div class="metric-list-item" onclick="useMetric('${metric.name}')">
                <div class="metric-name">${metric.name}</div>
                <div class="metric-description">${metric.description}</div>
            </div>
        `).join('');
        
    } catch (error) {
        console.error('Failed to load metrics:', error);
        metricsList.innerHTML = `
            <div class="loading-state">
                <i class="fas fa-exclamation-triangle"></i>
                <p>Failed to load metrics</p>
            </div>
        `;
    }
}

/**
 * Load key metrics data
 */
async function loadKeyMetrics() {
    try {
        // Simulate key metrics (in real implementation, use Prometheus API)
        const metrics = await simulateKeyMetrics();
        
        updateKeyMetrics(metrics);
        
    } catch (error) {
        console.error('Failed to load key metrics:', error);
    }
}

/**
 * Simulate key metrics loading
 */
async function simulateKeyMetrics() {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 500));
    
    return {
        chatRequests: Math.floor(Math.random() * 2000) + 1000,
        responseTime: (Math.random() * 3 + 1).toFixed(1),
        errorRate: (Math.random() * 2).toFixed(1),
        apiCost: (Math.random() * 50 + 10).toFixed(2),
        chatTrend: Math.random() > 0.5 ? '+5.2%' : '-2.1%',
        responseTrend: Math.random() > 0.3 ? '+12%' : '-8%',
        errorTrend: Math.random() > 0.7 ? '+1.2%' : '-1.2%',
        costTrend: Math.random() > 0.4 ? '+8.5%' : '-3.2%'
    };
}

/**
 * Update key metrics display
 */
function updateKeyMetrics(metrics) {
    const elements = {
        chatRequests: document.getElementById('chatRequests'),
        responseTime: document.getElementById('responseTime'),
        errorRate: document.getElementById('errorRate'),
        apiCost: document.getElementById('apiCost'),
        chatTrend: document.getElementById('chatTrend'),
        responseTrend: document.getElementById('responseTrend'),
        errorTrend: document.getElementById('errorTrend'),
        costTrend: document.getElementById('costTrend')
    };
    
    if (elements.chatRequests) {
        elements.chatRequests.textContent = metrics.chatRequests.toLocaleString();
    }
    
    if (elements.responseTime) {
        elements.responseTime.textContent = `${metrics.responseTime}s`;
    }
    
    if (elements.errorRate) {
        elements.errorRate.textContent = `${metrics.errorRate}%`;
    }
    
    if (elements.apiCost) {
        elements.apiCost.textContent = `$${metrics.apiCost}`;
    }
    
    // Update trends with appropriate classes
    updateTrend(elements.chatTrend, metrics.chatTrend);
    updateTrend(elements.responseTrend, metrics.responseTrend);
    updateTrend(elements.errorTrend, metrics.errorTrend);
    updateTrend(elements.costTrend, metrics.costTrend);
}

/**
 * Update trend indicator
 */
function updateTrend(element, trend) {
    if (!element) return;
    
    element.textContent = trend;
    element.className = 'metric-trend';
    
    if (trend.startsWith('+')) {
        element.classList.add('warning');
    } else if (trend.startsWith('-')) {
        element.classList.add('success');
    }
}

// ===== ACTION FUNCTIONS =====

/**
 * Refresh metrics
 */
async function refreshMetrics() {
    GenAI.showToast('Refreshing Prometheus metrics...', 'info');
    
    try {
        await Promise.all([
            checkPrometheusConnection(),
            loadKeyMetrics(),
            loadAvailableMetrics()
        ]);
        
        GenAI.showToast('Metrics refreshed successfully', 'success');
    } catch (error) {
        console.error('Failed to refresh metrics:', error);
        GenAI.showToast('Failed to refresh metrics', 'error');
    }
}

/**
 * Open Prometheus in new tab
 */
function openPrometheusNew() {
    window.open('http://localhost:9090', '_blank');
}

/**
 * Update time range
 */
function updateTimeRange() {
    const timeRange = document.getElementById('timeRange');
    if (timeRange) {
        currentTimeRange = timeRange.value;
        loadKeyMetrics(); // Reload metrics with new time range
        GenAI.showToast(`Time range updated to ${currentTimeRange}`, 'info');
    }
}

/**
 * Filter metrics list
 */
function filterMetrics() {
    const searchInput = document.getElementById('metricSearch');
    const metricItems = document.querySelectorAll('.metric-list-item');
    
    if (!searchInput) return;
    
    const searchTerm = searchInput.value.toLowerCase();
    
    metricItems.forEach(item => {
        const metricName = item.querySelector('.metric-name');
        const metricDescription = item.querySelector('.metric-description');
        
        if (metricName && metricDescription) {
            const nameMatch = metricName.textContent.toLowerCase().includes(searchTerm);
            const descMatch = metricDescription.textContent.toLowerCase().includes(searchTerm);
            
            item.style.display = (nameMatch || descMatch) ? 'block' : 'none';
        }
    });
}

/**
 * Use metric in query
 */
function useMetric(metricName) {
    const queryInput = document.getElementById('promqlQuery');
    if (queryInput) {
        queryInput.value = metricName;
        queryInput.focus();
    }
}

/**
 * Execute PromQL query
 */
async function executeQuery() {
    const queryInput = document.getElementById('promqlQuery');
    const resultsContainer = document.getElementById('queryResults');
    
    if (!queryInput || !resultsContainer) return;
    
    const query = queryInput.value.trim();
    if (!query) {
        GenAI.showToast('Please enter a PromQL query', 'warning');
        return;
    }
    
    resultsContainer.innerHTML = `
        <div class="loading-state">
            <i class="fas fa-spinner fa-spin"></i>
            <p>Executing query...</p>
        </div>
    `;
    
    try {
        // Simulate query execution (in real implementation, use Prometheus API)
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Simulate results
        const results = [
            { metric: '{instance="localhost:8000", job="genai-chatbot"}', value: [Date.now() / 1000, '1.234'] },
            { metric: '{instance="localhost:5000", job="mlflow"}', value: [Date.now() / 1000, '0.987'] },
            { metric: '{instance="localhost:9090", job="prometheus"}', value: [Date.now() / 1000, '2.456'] }
        ];
        
        resultsContainer.innerHTML = results.map(result => `
            <div class="query-result-item">
                <strong>${query}</strong>${result.metric} = ${result.value[1]}
            </div>
        `).join('');
        
        GenAI.showToast('Query executed successfully', 'success');
        
    } catch (error) {
        console.error('Query execution failed:', error);
        resultsContainer.innerHTML = `
            <div class="loading-state">
                <i class="fas fa-exclamation-triangle"></i>
                <p>Query execution failed</p>
            </div>
        `;
        GenAI.showToast('Query execution failed', 'error');
    }
}

/**
 * Show query examples modal
 */
function showQueryExamples() {
    const modal = document.getElementById('queryExamplesModal');
    if (modal) {
        modal.classList.add('active');
    }
}

/**
 * Close query examples modal
 */
function closeQueryExamples() {
    const modal = document.getElementById('queryExamplesModal');
    if (modal) {
        modal.classList.remove('active');
    }
}

/**
 * Use example query
 */
function useQuery(query) {
    const queryInput = document.getElementById('promqlQuery');
    if (queryInput) {
        queryInput.value = query;
    }
    closeQueryExamples();
}

/**
 * Toggle Prometheus fullscreen
 */
function togglePrometheusFullscreen() {
    const container = document.getElementById('prometheusContainer');
    const iframe = document.getElementById('prometheusIframe');
    
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
 * Refresh Prometheus iframe
 */
function refreshPrometheusIframe() {
    const iframe = document.getElementById('prometheusIframe');
    if (iframe) {
        iframe.src = iframe.src;
        GenAI.showToast('Prometheus console refreshed', 'info');
    }
}

// ===== EVENT LISTENERS =====

// Handle fullscreen changes
document.addEventListener('fullscreenchange', () => {
    const iframe = document.getElementById('prometheusIframe');
    if (iframe) {
        if (document.fullscreenElement) {
            iframe.style.height = '100vh';
        } else {
            iframe.style.height = '600px';
        }
    }
});

// Handle Enter key in query input
document.addEventListener('DOMContentLoaded', () => {
    const queryInput = document.getElementById('promqlQuery');
    if (queryInput) {
        queryInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
                executeQuery();
            }
        });
    }
});
