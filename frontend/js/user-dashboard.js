// User Dashboard functionality
class UserDashboard {
    constructor() {
        this.apiBase = window.API_BASE || 'http://localhost:8000';
        this.userSession = null;
        this.init();
    }

    async init() {
        this.checkAuthentication();
        this.loadUserSession();
        this.setupEventListeners();
        this.loadDashboardData();
    }

    checkAuthentication() {
        const session = localStorage.getItem('userSession');
        const isAuthenticated = sessionStorage.getItem('isAuthenticated');
        
        if (!session || !isAuthenticated) {
            window.location.href = 'login.html';
            return;
        }
        
        try {
            const sessionData = JSON.parse(session);
            const now = new Date();
            const expiresAt = new Date(sessionData.expiresAt);
            
            if (now >= expiresAt) {
                this.logout();
                return;
            }
            
            if (sessionData.role !== 'user' && sessionData.role !== 'admin') {
                window.location.href = 'login.html';
                return;
            }
            
            this.userSession = sessionData;
        } catch (error) {
            console.error('Error parsing session:', error);
            this.logout();
        }
    }

    loadUserSession() {
        if (!this.userSession) return;
        
        const userName = this.userSession.username;
        const displayName = this.getDisplayName(userName);
        
        // Update UI with user info
        document.getElementById('userName').textContent = displayName;
        document.getElementById('userDisplayName').textContent = displayName;
        document.getElementById('dropdownUserName').textContent = displayName;
        
        // Update welcome message
        const welcomeText = document.querySelector('.welcome-text');
        if (welcomeText) {
            welcomeText.innerHTML = `Welcome back, <span id="userName">${displayName}</span>!`;
        }
        
        // Show admin access option if user is admin
        if (this.userSession.role === 'admin') {
            const adminAccess = document.querySelector('.admin-access');
            if (adminAccess) {
                adminAccess.style.display = 'flex';
            }
        }
    }

    setupEventListeners() {
        // User menu toggle
        const userMenuBtn = document.getElementById('userMenuBtn');
        const userDropdown = document.getElementById('userDropdown');
        
        if (userMenuBtn && userDropdown) {
            userMenuBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                userDropdown.classList.toggle('show');
            });
            
            // Close dropdown when clicking outside
            document.addEventListener('click', () => {
                userDropdown.classList.remove('show');
            });
        }
        
        // Mode card selection
        const modeCards = document.querySelectorAll('.mode-card');
        modeCards.forEach(card => {
            card.addEventListener('click', () => {
                modeCards.forEach(c => c.classList.remove('active'));
                card.classList.add('active');
            });
        });
        
        // Auto-refresh stats every 30 seconds
        setInterval(() => {
            this.loadDashboardData();
        }, 30000);
    }

    async loadDashboardData() {
        try {
            // Load user statistics
            await this.loadUserStats();
            await this.loadRecentChats();
        } catch (error) {
            console.error('Error loading dashboard data:', error);
        }
    }

    async loadUserStats() {
        try {
            // Mock data - in production, this would come from your API
            const stats = {
                totalChats: this.getChatCount(),
                documentsUploaded: this.getDocumentCount(),
                avgResponseTime: '1.2s',
                sessionsToday: 1
            };
            
            // Update stat cards
            document.getElementById('totalChats').textContent = stats.totalChats;
            document.getElementById('documentsUploaded').textContent = stats.documentsUploaded;
            document.getElementById('avgResponseTime').textContent = stats.avgResponseTime;
            document.getElementById('sessionsToday').textContent = stats.sessionsToday;
            
        } catch (error) {
            console.error('Error loading user stats:', error);
        }
    }

    async loadRecentChats() {
        try {
            // Load recent chats from localStorage
            const chatHistory = JSON.parse(localStorage.getItem('chatHistory') || '[]');
            const recentChats = chatHistory.slice(-5).reverse(); // Get last 5 chats
            
            const recentChatsContainer = document.getElementById('recentChats');
            if (recentChats.length === 0) {
                recentChatsContainer.innerHTML = `
                    <div class="empty-state">
                        <i class="fas fa-comments"></i>
                        <p>No recent conversations</p>
                        <small>Start a new chat to see your conversation history here</small>
                    </div>
                `;
            } else {
                // Render recent chats (keeping existing mock data for now)
                // In production, this would render actual chat data
            }
        } catch (error) {
            console.error('Error loading recent chats:', error);
        }
    }

    getChatCount() {
        try {
            const chatHistory = JSON.parse(localStorage.getItem('chatHistory') || '[]');
            return chatHistory.length;
        } catch {
            return 0;
        }
    }

    getDocumentCount() {
        try {
            // Count uploaded files from localStorage
            const uploadedFiles = JSON.parse(localStorage.getItem('uploadedFiles') || '[]');
            return uploadedFiles.length;
        } catch {
            return 0;
        }
    }

    getDisplayName(username) {
        // Get display name from localStorage or use username
        const savedProfile = localStorage.getItem('userProfile');
        if (savedProfile) {
            try {
                const profile = JSON.parse(savedProfile);
                return profile.displayName || username;
            } catch {
                return username;
            }
        }
        return username;
    }

    // UI Actions  
    startChat(mode) {
        console.log('Starting chat with mode:', mode);
        
        // Save selected mode
        localStorage.setItem('selectedChatMode', mode);
        
        // Show loading message
        this.showToast(`Starting ${mode === 'rag' ? 'RAG' : 'Direct'} mode chat...`, 'info');
        
        // Redirect to chat page after a brief delay
        setTimeout(() => {
            window.location.href = 'chat.html';
        }, 500);
    }

    continueChat(chatId) {
        // Load specific chat and redirect
        localStorage.setItem('continueChatId', chatId);
        window.location.href = 'chat.html';
    }

    showProfile() {
        const modal = document.getElementById('profileModal');
        if (modal) {
            modal.classList.add('show');
            
            // Load current profile data
            const savedProfile = localStorage.getItem('userProfile');
            if (savedProfile) {
                try {
                    const profile = JSON.parse(savedProfile);
                    document.getElementById('profileDisplayName').value = profile.displayName || '';
                    document.getElementById('preferredMode').value = profile.preferredMode || 'direct';
                    document.getElementById('emailNotifications').checked = profile.emailNotifications || false;
                    document.getElementById('soundNotifications').checked = profile.soundNotifications || false;
                } catch (error) {
                    console.error('Error loading profile:', error);
                }
            }
        }
    }

    saveProfile() {
        try {
            const profile = {
                displayName: document.getElementById('profileDisplayName').value,
                preferredMode: document.getElementById('preferredMode').value,
                emailNotifications: document.getElementById('emailNotifications').checked,
                soundNotifications: document.getElementById('soundNotifications').checked,
                updatedAt: new Date().toISOString()
            };
            
            localStorage.setItem('userProfile', JSON.stringify(profile));
            
            // Update UI with new display name
            if (profile.displayName) {
                document.getElementById('userName').textContent = profile.displayName;
                document.getElementById('userDisplayName').textContent = profile.displayName;
                document.getElementById('dropdownUserName').textContent = profile.displayName;
            }
            
            this.closeModal('profileModal');
            this.showToast('Profile updated successfully!', 'success');
            
        } catch (error) {
            console.error('Error saving profile:', error);
            this.showToast('Error saving profile', 'error');
        }
    }

    showChatHistory() {
        // Redirect to chat page with history view
        window.location.href = 'chat.html?view=history';
    }

    switchToAdmin() {
        if (this.userSession && this.userSession.role === 'admin') {
            // Update session to admin mode and redirect
            this.userSession.currentView = 'admin';
            localStorage.setItem('userSession', JSON.stringify(this.userSession));
            window.location.href = 'index.html';
        } else {
            this.showToast('Admin access not available', 'error');
        }
    }

    quickAction(action) {
        switch (action) {
            case 'help':
                this.startChat('direct');
                // Pre-fill with help message
                setTimeout(() => {
                    const chatInput = document.getElementById('chatInput');
                    if (chatInput) {
                        chatInput.value = 'What can you help me with?';
                    }
                }, 1000);
                break;
                
            case 'upload':
                this.startChat('rag');
                break;
                
            case 'templates':
                this.showToast('Chat templates coming soon!', 'info');
                break;
                
            case 'export':
                this.exportChatHistory();
                break;
        }
    }

    exportChatHistory() {
        try {
            const chatHistory = JSON.parse(localStorage.getItem('chatHistory') || '[]');
            if (chatHistory.length === 0) {
                this.showToast('No chat history to export', 'info');
                return;
            }
            
            const exportData = {
                user: this.userSession.username,
                exportDate: new Date().toISOString(),
                totalChats: chatHistory.length,
                chatHistory: chatHistory
            };
            
            const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `chat-history-${new Date().toISOString().split('T')[0]}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            
            this.showToast('Chat history exported successfully!', 'success');
            
        } catch (error) {
            console.error('Error exporting chat history:', error);
            this.showToast('Error exporting chat history', 'error');
        }
    }

    closeModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.remove('show');
        }
    }

    logout() {
        // Clear session data
        localStorage.removeItem('userSession');
        sessionStorage.removeItem('isAuthenticated');
        
        // Show logout message and redirect
        this.showToast('Logged out successfully', 'info');
        setTimeout(() => {
            window.location.href = 'login.html';
        }, 1000);
    }

    showToast(message, type = 'info') {
        // Create toast notification
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
            <span>${message}</span>
        `;

        document.body.appendChild(toast);

        // Auto remove after 3 seconds
        setTimeout(() => {
            toast.style.animation = 'slideOutRight 0.3s ease forwards';
            setTimeout(() => {
                if (document.body.contains(toast)) {
                    document.body.removeChild(toast);
                }
            }, 300);
        }, 3000);
    }
}

// Global functions for HTML onclick handlers
function startChat(mode) {
    if (window.userDashboard) {
        window.userDashboard.startChat(mode);
    }
}

function continueChat(chatId) {
    if (window.userDashboard) {
        window.userDashboard.continueChat(chatId);
    }
}

function showProfile() {
    if (window.userDashboard) {
        window.userDashboard.showProfile();
    }
}

function saveProfile() {
    if (window.userDashboard) {
        window.userDashboard.saveProfile();
    }
}

function showChatHistory() {
    if (window.userDashboard) {
        window.userDashboard.showChatHistory();
    }
}

function switchToAdmin() {
    if (window.userDashboard) {
        window.userDashboard.switchToAdmin();
    }
}

function quickAction(action) {
    if (window.userDashboard) {
        window.userDashboard.quickAction(action);
    }
}

function closeModal(modalId) {
    if (window.userDashboard) {
        window.userDashboard.closeModal(modalId);
    }
}

function logout() {
    if (window.userDashboard) {
        window.userDashboard.logout();
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.userDashboard = new UserDashboard();
});
