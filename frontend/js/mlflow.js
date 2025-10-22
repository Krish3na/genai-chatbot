// MLflow Dashboard Integration
class MLflowDashboard {
    constructor() {
        this.apiBase = window.API_BASE || 'http://localhost:8000';
        this.mlflowBase = 'http://localhost:5000';
        this.currentView = 'embedded';
        this.connectionRetries = 0;
        this.maxRetries = 3;
        this.init();
    }

    async init() {
        this.setupEventListeners();
        await this.checkMLflowConnection();
        this.loadDashboardData();
        this.startAutoRefresh();
    }

    setupEventListeners() {
        // View switching
        document.querySelectorAll('.option-card').forEach(card => {
            card.addEventListener('click', (e) => this.switchView(e.target.closest('.option-card').dataset.view));
        });

        // Iframe load handling
        const iframe = document.getElementById('mlflowFrame');
        if (iframe) {
            iframe.addEventListener('load', () => this.handleIframeLoad());
            iframe.addEventListener('error', () => this.handleIframeError());
        }

        // Window resize handling for iframe
        window.addEventListener('resize', () => this.adjustIframeHeight());
    }

    async checkMLflowConnection() {
        try {
            const response = await fetch(`${this.mlflowBase}/api/2.0/mlflow/experiments/list`, {
                method: 'GET',
                mode: 'cors'
            });
            
            if (response.ok) {
                this.hideConnectionModal();
                return true;
            } else {
                throw new Error('MLflow server not responding');
            }
        } catch (error) {
            console.warn('MLflow connection failed:', error);
            this.showConnectionModal();
            return false;
        }
    }

    switchView(viewType) {
        // Update active option card
        document.querySelectorAll('.option-card').forEach(card => {
            card.classList.remove('active');
        });
        document.querySelector(`[data-view="${viewType}"]`).classList.add('active');

        // Switch views
        document.querySelectorAll('.embedded-view, .api-view').forEach(view => {
            view.classList.remove('active');
        });

        this.currentView = viewType;

        switch (viewType) {
            case 'embedded':
                document.getElementById('embeddedView').classList.add('active');
                this.refreshIframe();
                break;
            case 'new-tab':
                this.openInNewTab();
                // Switch back to embedded view
                setTimeout(() => this.switchView('embedded'), 100);
                break;
            case 'api-data':
                document.getElementById('apiView').classList.add('active');
                this.loadAPIData();
                break;
        }
    }

    async loadDashboardData() {
        try {
            await Promise.all([
                this.loadExperimentStats(),
                this.loadRunStats(),
                this.loadPerformanceMetrics()
            ]);
        } catch (error) {
            console.error('Error loading dashboard data:', error);
        }
    }

    async loadExperimentStats() {
        try {
            const response = await fetch(`${this.apiBase}/mlflow/experiments`);
            if (response.ok) {
                const data = await response.json();
                this.updateStatCard('totalExperiments', data.total_experiments || 0);
            }
        } catch (error) {
            console.error('Error loading experiment stats:', error);
            this.updateStatCard('totalExperiments', 'N/A');
        }
    }

    async loadRunStats() {
        try {
            // Try to get runs data from our API
            const response = await fetch(`${this.apiBase}/mlflow/best-run`);
            if (response.ok) {
                const data = await response.json();
                this.updateStatCard('totalRuns', data.total_runs || 0);
                this.updateStatCard('avgResponseTime', `${(data.avg_response_time || 0).toFixed(0)}ms`);
                this.updateStatCard('avgAccuracy', `${((data.avg_accuracy || 0) * 100).toFixed(1)}%`);
            }
        } catch (error) {
            console.error('Error loading run stats:', error);
            this.updateStatCard('totalRuns', 'N/A');
        }
    }

    async loadPerformanceMetrics() {
        try {
            const response = await fetch(`${this.apiBase}/mlflow/model-performance`);
            if (response.ok) {
                const data = await response.json();
                // Update performance indicators
                console.log('Performance metrics:', data);
            }
        } catch (error) {
            console.error('Error loading performance metrics:', error);
        }
    }

    async loadAPIData() {
        await Promise.all([
            this.loadExperimentsData(),
            this.loadRunsData(),
            this.loadPerformanceData()
        ]);
    }

    async loadExperimentsData() {
        const container = document.getElementById('experimentsData');
        try {
            const response = await fetch(`${this.apiBase}/mlflow/experiments`);
            if (response.ok) {
                const data = await response.json();
                container.innerHTML = this.renderExperimentsTable(data.experiments || []);
            } else {
                throw new Error('Failed to load experiments');
            }
        } catch (error) {
            container.innerHTML = `
                <div class="error-state">
                    <i class="fas fa-exclamation-triangle"></i>
                    <p>Failed to load experiments</p>
                    <button class="btn btn-sm" onclick="mlflowDashboard.loadExperimentsData()">
                        <i class="fas fa-retry"></i> Retry
                    </button>
                </div>
            `;
        }
    }

    async loadRunsData() {
        const container = document.getElementById('runsData');
        try {
            const response = await fetch(`${this.apiBase}/mlflow/best-run`);
            if (response.ok) {
                const data = await response.json();
                container.innerHTML = this.renderRunsTable([data]);
            } else {
                throw new Error('Failed to load runs');
            }
        } catch (error) {
            container.innerHTML = `
                <div class="error-state">
                    <i class="fas fa-exclamation-triangle"></i>
                    <p>Failed to load runs</p>
                    <button class="btn btn-sm" onclick="mlflowDashboard.loadRunsData()">
                        <i class="fas fa-retry"></i> Retry
                    </button>
                </div>
            `;
        }
    }

    async loadPerformanceData() {
        const container = document.getElementById('performanceData');
        try {
            const response = await fetch(`${this.apiBase}/mlflow/model-performance`);
            if (response.ok) {
                const data = await response.json();
                container.innerHTML = this.renderPerformanceMetrics(data);
            } else {
                throw new Error('Failed to load performance data');
            }
        } catch (error) {
            container.innerHTML = `
                <div class="error-state">
                    <i class="fas fa-exclamation-triangle"></i>
                    <p>Failed to load performance data</p>
                    <button class="btn btn-sm" onclick="mlflowDashboard.loadPerformanceData()">
                        <i class="fas fa-retry"></i> Retry
                    </button>
                </div>
            `;
        }
    }

    renderExperimentsTable(experiments) {
        if (!experiments.length) {
            return `
                <div class="empty-state">
                    <i class="fas fa-flask"></i>
                    <p>No experiments found</p>
                </div>
            `;
        }

        return `
            <div class="data-table">
                <table>
                    <thead>
                        <tr>
                            <th>Experiment ID</th>
                            <th>Name</th>
                            <th>Lifecycle Stage</th>
                            <th>Created</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${experiments.map(exp => `
                            <tr>
                                <td>${exp.experiment_id}</td>
                                <td>${exp.name}</td>
                                <td><span class="status-badge ${exp.lifecycle_stage}">${exp.lifecycle_stage}</span></td>
                                <td>${new Date(exp.creation_time).toLocaleDateString()}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
    }

    renderRunsTable(runs) {
        if (!runs.length) {
            return `
                <div class="empty-state">
                    <i class="fas fa-play"></i>
                    <p>No runs found</p>
                </div>
            `;
        }

        return `
            <div class="data-table">
                <table>
                    <thead>
                        <tr>
                            <th>Run ID</th>
                            <th>Status</th>
                            <th>Response Time</th>
                            <th>Accuracy</th>
                            <th>Cost</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${runs.map(run => `
                            <tr>
                                <td><code>${(run.run_id || 'N/A').substring(0, 8)}...</code></td>
                                <td><span class="status-badge ${run.status || 'unknown'}">${run.status || 'Unknown'}</span></td>
                                <td>${(run.avg_response_time || 0).toFixed(0)}ms</td>
                                <td>${((run.avg_accuracy || 0) * 100).toFixed(1)}%</td>
                                <td>$${(run.total_cost || 0).toFixed(4)}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
    }

    renderPerformanceMetrics(data) {
        return `
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-icon">
                        <i class="fas fa-clock"></i>
                    </div>
                    <div class="metric-content">
                        <h4>Response Time</h4>
                        <span class="metric-value">${(data.avg_response_time || 0).toFixed(0)}ms</span>
                        <span class="metric-trend ${data.response_time_trend || 'neutral'}">
                            <i class="fas fa-arrow-${data.response_time_trend === 'up' ? 'up' : 'down'}"></i>
                            ${data.response_time_change || 0}%
                        </span>
                    </div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-icon">
                        <i class="fas fa-bullseye"></i>
                    </div>
                    <div class="metric-content">
                        <h4>Accuracy</h4>
                        <span class="metric-value">${((data.avg_accuracy || 0) * 100).toFixed(1)}%</span>
                        <span class="metric-trend ${data.accuracy_trend || 'neutral'}">
                            <i class="fas fa-arrow-${data.accuracy_trend === 'up' ? 'up' : 'down'}"></i>
                            ${data.accuracy_change || 0}%
                        </span>
                    </div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-icon">
                        <i class="fas fa-dollar-sign"></i>
                    </div>
                    <div class="metric-content">
                        <h4>Total Cost</h4>
                        <span class="metric-value">$${(data.total_cost || 0).toFixed(4)}</span>
                        <span class="metric-trend ${data.cost_trend || 'neutral'}">
                            <i class="fas fa-arrow-${data.cost_trend === 'up' ? 'up' : 'down'}"></i>
                            ${data.cost_change || 0}%
                        </span>
                    </div>
                </div>
            </div>
        `;
    }

    // Iframe management
    handleIframeLoad() {
        const loading = document.querySelector('.iframe-loading');
        if (loading) {
            loading.style.display = 'none';
        }
    }

    handleIframeError() {
        const loading = document.querySelector('.iframe-loading');
        if (loading) {
            loading.innerHTML = `
                <i class="fas fa-exclamation-triangle"></i>
                <p>Failed to load MLflow UI</p>
                <button class="btn btn-sm" onclick="mlflowDashboard.refreshIframe()">
                    <i class="fas fa-retry"></i> Retry
                </button>
            `;
        }
    }

    refreshIframe() {
        const iframe = document.getElementById('mlflowFrame');
        const loading = document.querySelector('.iframe-loading');
        
        if (loading) {
            loading.style.display = 'flex';
            loading.innerHTML = `
                <i class="fas fa-spinner fa-spin"></i>
                <p>Refreshing MLflow Dashboard...</p>
            `;
        }
        
        if (iframe) {
            iframe.src = iframe.src;
        }
    }

    openInNewTab() {
        window.open(this.mlflowBase, '_blank');
    }

    toggleFullscreen() {
        const container = document.querySelector('.iframe-container');
        if (container) {
            container.classList.toggle('fullscreen');
            const icon = document.querySelector('[onclick="toggleFullscreen()"] i');
            if (icon) {
                icon.className = container.classList.contains('fullscreen') ? 
                    'fas fa-compress' : 'fas fa-expand';
            }
        }
    }

    // Modal management
    showConnectionModal() {
        const modal = document.getElementById('connectionModal');
        if (modal) {
            modal.classList.add('show');
        }
    }

    hideConnectionModal() {
        const modal = document.getElementById('connectionModal');
        if (modal) {
            modal.classList.remove('show');
        }
    }

    async retryConnection() {
        if (this.connectionRetries < this.maxRetries) {
            this.connectionRetries++;
            const connected = await this.checkMLflowConnection();
            if (connected) {
                this.connectionRetries = 0;
                this.refreshIframe();
                this.loadDashboardData();
            }
        } else {
            this.showToast('Maximum retry attempts reached. Please check MLflow server.', 'error');
        }
    }

    // Utility functions
    updateStatCard(id, value) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
            element.style.animation = 'pulse 0.3s ease-in-out';
        }
    }

    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check' : type === 'error' ? 'exclamation-triangle' : 'info-circle'}"></i>
            <span>${message}</span>
        `;

        document.body.appendChild(toast);

        setTimeout(() => {
            toast.style.animation = 'slideOutRight 0.3s ease forwards';
            setTimeout(() => document.body.removeChild(toast), 300);
        }, 3000);
    }

    startAutoRefresh() {
        // Auto-refresh every 30 seconds
        setInterval(() => {
            if (this.currentView === 'api-data') {
                this.loadAPIData();
            }
            this.loadDashboardData();
        }, 30000);
    }
}

// Global functions for buttons
function refreshMLflowData() {
    if (window.mlflowDashboard) {
        window.mlflowDashboard.loadDashboardData();
        if (window.mlflowDashboard.currentView === 'api-data') {
            window.mlflowDashboard.loadAPIData();
        }
    }
}

function openMLflowUI() {
    window.open('http://localhost:5000', '_blank');
}

function refreshIframe() {
    if (window.mlflowDashboard) {
        window.mlflowDashboard.refreshIframe();
    }
}

function openInNewTab() {
    if (window.mlflowDashboard) {
        window.mlflowDashboard.openInNewTab();
    }
}

function toggleFullscreen() {
    if (window.mlflowDashboard) {
        window.mlflowDashboard.toggleFullscreen();
    }
}

function retryConnection() {
    if (window.mlflowDashboard) {
        window.mlflowDashboard.retryConnection();
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('show');
    }
}

// Quick action functions
function createNewExperiment() {
    window.open('http://localhost:5000/#/experiments/create', '_blank');
}

function viewBestRuns() {
    window.open('http://localhost:5000/#/experiments/0', '_blank');
}

function exportMetrics() {
    if (window.mlflowDashboard) {
        window.mlflowDashboard.showToast('Export functionality coming soon!', 'info');
    }
}

function compareRuns() {
    window.open('http://localhost:5000/#/compare-runs', '_blank');
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.mlflowDashboard = new MLflowDashboard();
});
