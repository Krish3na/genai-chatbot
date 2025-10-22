// ===== ALERTS PAGE JAVASCRIPT =====

let alertsData = null;
let thresholdsData = null;
let currentFilter = 'all';

// ===== INITIALIZATION =====
document.addEventListener('DOMContentLoaded', () => {
    initializeAlertsPage();
});

async function initializeAlertsPage() {
    console.log('Initializing alerts page');
    
    // Initialize filter buttons
    initializeFilterButtons();
    
    // Load initial data
    await loadAlertsData();
    await loadThresholdsData();
    await loadEmailConfiguration();
    
    // Set up auto-refresh
    setInterval(loadAlertsData, 30000); // Refresh every 30 seconds
}

// ===== FILTER FUNCTIONALITY =====
function initializeFilterButtons() {
    const filterButtons = document.querySelectorAll('.filter-btn');
    filterButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            // Update active state
            filterButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            // Update filter
            currentFilter = btn.dataset.filter;
            renderAlerts();
        });
    });
}

// ===== DATA LOADING FUNCTIONS =====

/**
 * Load alerts data from API
 */
async function loadAlertsData() {
    try {
        const response = await GenAI.apiRequest('/alerts/check');
        alertsData = response;
        
        updateStatusCards(response);
        renderAlerts();
        
    } catch (error) {
        console.error('Failed to load alerts:', error);
        showAlertsError('Failed to load alerts. Make sure the system is running.');
    }
}

/**
 * Load thresholds data from API
 */
async function loadThresholdsData() {
    try {
        const response = await GenAI.apiRequest('/alerts/thresholds');
        thresholdsData = response.thresholds;
        
        renderThresholds();
        
    } catch (error) {
        console.error('Failed to load thresholds:', error);
        showThresholdsError('Failed to load thresholds.');
    }
}

/**
 * Load email configuration
 */
async function loadEmailConfiguration() {
    try {
        const response = await GenAI.apiRequest('/alerts/email-config');
        updateEmailConfiguration(response);
        
    } catch (error) {
        console.error('Failed to load email configuration:', error);
        updateEmailConfiguration({
            email_alerts_enabled: false,
            sender_configured: false,
            recipients: ['saikrishna.sriram3@gmail.com']
        });
    }
}

// ===== UI UPDATE FUNCTIONS =====

/**
 * Update status cards with alert data
 */
function updateStatusCards(data) {
    // System status
    const systemStatusText = document.getElementById('systemStatusText');
    if (systemStatusText) {
        systemStatusText.textContent = data.status || 'Unknown';
        systemStatusText.className = getStatusClass(data.status);
    }
    
    // Total alerts
    const totalAlertsCount = document.getElementById('totalAlertsCount');
    if (totalAlertsCount) {
        totalAlertsCount.textContent = data.total_alerts || 0;
    }
    
    // Count critical and warning alerts
    let criticalCount = 0;
    let warningCount = 0;
    
    if (data.alerts) {
        Object.values(data.alerts).forEach(alertList => {
            alertList.forEach(alert => {
                if (alert.type === 'CRITICAL') {
                    criticalCount++;
                } else if (alert.type === 'WARNING') {
                    warningCount++;
                }
            });
        });
    }
    
    const criticalAlertsCount = document.getElementById('criticalAlertsCount');
    if (criticalAlertsCount) {
        criticalAlertsCount.textContent = criticalCount;
    }
    
    const warningAlertsCount = document.getElementById('warningAlertsCount');
    if (warningAlertsCount) {
        warningAlertsCount.textContent = warningCount;
    }
}

/**
 * Render alerts list
 */
function renderAlerts() {
    const container = document.getElementById('activeAlerts');
    if (!container || !alertsData) return;
    
    const allAlerts = [];
    
    // Flatten alerts from all categories
    if (alertsData.alerts) {
        Object.entries(alertsData.alerts).forEach(([category, alerts]) => {
            alerts.forEach(alert => {
                allAlerts.push({
                    ...alert,
                    category: category
                });
            });
        });
    }
    
    // Filter alerts
    const filteredAlerts = allAlerts.filter(alert => {
        if (currentFilter === 'all') return true;
        if (currentFilter === 'critical') return alert.type === 'CRITICAL';
        if (currentFilter === 'warning') return alert.type === 'WARNING';
        return true;
    });
    
    if (filteredAlerts.length === 0) {
        container.innerHTML = `
            <div class="no-data-state">
                <i class="fas fa-check-circle"></i>
                <p>No ${currentFilter === 'all' ? '' : currentFilter.toLowerCase() + ' '}alerts found</p>
            </div>
        `;
        return;
    }
    
    // Sort alerts by type (critical first) then by timestamp
    filteredAlerts.sort((a, b) => {
        if (a.type !== b.type) {
            return a.type === 'CRITICAL' ? -1 : 1;
        }
        return (b.timestamp || 0) - (a.timestamp || 0);
    });
    
    container.innerHTML = filteredAlerts.map(alert => `
        <div class="alert-item ${alert.type.toLowerCase()}">
            <div class="alert-timestamp">${GenAI.formatTimestamp(alert.timestamp || Date.now() / 1000)}</div>
            <div class="alert-header">
                <span class="alert-type-badge ${alert.type.toLowerCase()}">${alert.type}</span>
                <span class="alert-category">${alert.category} | ${alert.metric}</span>
            </div>
            <div class="alert-metric">
                <strong>Value:</strong> ${alert.value} | <strong>Threshold:</strong> ${alert.threshold}
            </div>
            <div class="alert-message">${alert.message}</div>
        </div>
    `).join('');
}

/**
 * Render thresholds list
 */
function renderThresholds() {
    const container = document.getElementById('thresholdsList');
    if (!container || !thresholdsData) return;
    
    const thresholdEntries = Object.entries(thresholdsData);
    
    if (thresholdEntries.length === 0) {
        container.innerHTML = `
            <div class="no-data-state">
                <i class="fas fa-sliders-h"></i>
                <p>No thresholds configured</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = thresholdEntries.map(([key, value]) => `
        <div class="threshold-item">
            <span class="threshold-name">${formatThresholdName(key)}</span>
            <span class="threshold-value">${formatThresholdValue(key, value)}</span>
        </div>
    `).join('');
}

/**
 * Update email configuration display
 */
function updateEmailConfiguration(config) {
    // Email status
    const emailStatusText = document.getElementById('emailStatusText');
    if (emailStatusText) {
        if (config.email_alerts_enabled && config.sender_configured) {
            emailStatusText.textContent = '✅ Active';
        } else if (config.email_alerts_enabled) {
            emailStatusText.textContent = '⚠️ Config Needed';
        } else {
            emailStatusText.textContent = '❌ Disabled';
        }
    }
    
    // Configuration details
    const emailConfigStatus = document.getElementById('emailConfigStatus');
    if (emailConfigStatus) {
        const isConfigured = config.email_alerts_enabled && config.sender_configured;
        emailConfigStatus.textContent = isConfigured ? 'Configured' : 'Not Configured';
        emailConfigStatus.className = `status-badge ${isConfigured ? 'configured' : 'not-configured'}`;
    }
    
    const emailRecipients = document.getElementById('emailRecipients');
    if (emailRecipients && config.recipients) {
        emailRecipients.textContent = config.recipients.join(', ');
    }
    
    const smtpServer = document.getElementById('smtpServer');
    if (smtpServer) {
        smtpServer.textContent = config.smtp_server || 'smtp.gmail.com';
    }
}

// ===== ERROR HANDLING =====

function showAlertsError(message) {
    const container = document.getElementById('activeAlerts');
    if (container) {
        container.innerHTML = `
            <div class="loading-state">
                <i class="fas fa-exclamation-triangle"></i>
                <p>${message}</p>
            </div>
        `;
    }
}

function showThresholdsError(message) {
    const container = document.getElementById('thresholdsList');
    if (container) {
        container.innerHTML = `
            <div class="loading-state">
                <i class="fas fa-exclamation-triangle"></i>
                <p>${message}</p>
            </div>
        `;
    }
}

// ===== UTILITY FUNCTIONS =====

function getStatusClass(status) {
    const classes = {
        healthy: 'text-success',
        warning: 'text-warning',
        critical: 'text-danger',
        error: 'text-danger'
    };
    return classes[status] || '';
}

function formatThresholdName(key) {
    return key
        .replace(/_/g, ' ')
        .replace(/\b\w/g, l => l.toUpperCase());
}

function formatThresholdValue(key, value) {
    if (key.includes('time')) {
        return `${value}s`;
    } else if (key.includes('accuracy')) {
        return `${value}%`;
    } else if (key.includes('cost')) {
        return GenAI.formatCost(value);
    } else if (key.includes('rate')) {
        return `${value}%`;
    }
    return value.toString();
}

// ===== ACTION FUNCTIONS =====

/**
 * Check alerts manually
 */
async function checkAlerts() {
    GenAI.showToast('Checking alerts...', 'info');
    await loadAlertsData();
    GenAI.showToast('Alerts refreshed', 'success');
}

/**
 * Test email functionality
 */
async function testEmail() {
    try {
        GenAI.showToast('Sending test email...', 'info');
        
        const response = await GenAI.apiRequest('/alerts/test-email', {
            method: 'POST'
        });
        
        GenAI.showToast(`Test email sent to: ${response.recipients.join(', ')}`, 'success');
        
    } catch (error) {
        console.error('Failed to send test email:', error);
        GenAI.showToast('Failed to send test email. Check configuration.', 'error');
    }
}

/**
 * Test email alert
 */
async function testEmailAlert() {
    await testEmail();
}

/**
 * Open MLflow UI
 */
function openMLflow() {
    GenAI.openMLflow();
}

/**
 * Edit thresholds
 */
function editThresholds() {
    const modal = document.getElementById('thresholdModal');
    if (modal && thresholdsData) {
        // Populate form with current values
        populateThresholdForm();
        modal.classList.add('active');
    }
}

/**
 * Close threshold modal
 */
function closeThresholdModal() {
    const modal = document.getElementById('thresholdModal');
    if (modal) {
        modal.classList.remove('active');
    }
}

/**
 * Populate threshold form with current values
 */
function populateThresholdForm() {
    if (!thresholdsData) return;
    
    const fieldMappings = {
        'response_time_warning': 'responseTimeWarning',
        'response_time_critical': 'responseTimeCritical',
        'accuracy_warning': 'accuracyWarning',
        'accuracy_critical': 'accuracyCritical',
        'daily_cost_warning': 'dailyCostWarning',
        'daily_cost_critical': 'dailyCostCritical'
    };
    
    Object.entries(fieldMappings).forEach(([key, fieldId]) => {
        const field = document.getElementById(fieldId);
        if (field && thresholdsData[key] !== undefined) {
            field.value = thresholdsData[key];
        }
    });
}

/**
 * Save threshold changes
 */
async function saveThresholds() {
    try {
        const formData = new FormData(document.getElementById('thresholdForm'));
        const updates = {};
        
        const fieldMappings = {
            'responseTimeWarning': 'response_time_warning',
            'responseTimeCritical': 'response_time_critical',
            'accuracyWarning': 'accuracy_warning',
            'accuracyCritical': 'accuracy_critical',
            'dailyCostWarning': 'daily_cost_warning',
            'dailyCostCritical': 'daily_cost_critical'
        };
        
        Object.entries(fieldMappings).forEach(([fieldId, key]) => {
            const field = document.getElementById(fieldId);
            if (field && field.value) {
                updates[key] = parseFloat(field.value);
            }
        });
        
        GenAI.showToast('Saving thresholds...', 'info');
        
        await GenAI.apiRequest('/alerts/thresholds', {
            method: 'POST',
            body: JSON.stringify(updates)
        });
        
        GenAI.showToast('Thresholds updated successfully', 'success');
        closeThresholdModal();
        await loadThresholdsData();
        
    } catch (error) {
        console.error('Failed to save thresholds:', error);
        GenAI.showToast('Failed to save thresholds', 'error');
    }
}

/**
 * Configure email alerts
 */
function configureEmail() {
    GenAI.showToast('Email configuration guide coming soon!', 'info');
    // TODO: Implement email configuration modal
}

/**
 * View email setup guide
 */
function viewEmailGuide() {
    const guideUrl = 'Setup_Your_Email_Alerts.md';
    window.open(guideUrl, '_blank');
}
