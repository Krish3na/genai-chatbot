// Enhanced Login System with Authentication
class LoginSystem {
    constructor() {
        this.users = {
            // User credentials - in production, this should be handled by backend
            'demo_user': { password: 'chat123', role: 'user' },
            'user1': { password: '123', role: 'user' },
            'testuser': { password: 'test123', role: 'user' },
            // Admin credentials can also login as users
            'admin': { password: 'admin2024', role: 'user', isAdmin: true },
            'administrator': { password: 'secure123', role: 'user', isAdmin: true }
        };
        
        this.admins = {
            // Admin credentials - in production, this should be handled by backend
            'admin': { password: 'admin2024', role: 'admin' },
            'administrator': { password: 'secure123', role: 'admin' }
        };
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.checkExistingSession();
    }

    setupEventListeners() {
        // Form submissions
        const userForm = document.getElementById('userForm');
        const adminForm = document.getElementById('adminForm');

        if (userForm) {
            userForm.addEventListener('submit', (e) => this.handleUserLogin(e));
        }

        if (adminForm) {
            adminForm.addEventListener('submit', (e) => this.handleAdminLogin(e));
        }

        // Demo credential click-to-fill
        this.setupDemoCredentials();
        
        // Enter key handling
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                const activeForm = document.querySelector('.login-form-container:not(.admin-form)') || 
                                 document.querySelector('.login-form-container.admin-form');
                if (activeForm && activeForm.style.display !== 'none') {
                    const submitBtn = activeForm.querySelector('.login-btn');
                    if (submitBtn) submitBtn.click();
                }
            }
        });
    }

    setupDemoCredentials() {
        // Make demo credentials clickable
        const credItems = document.querySelectorAll('.cred-item');
        credItems.forEach(item => {
            item.style.cursor = 'pointer';
            item.title = 'Click to auto-fill credentials';
            
            item.addEventListener('click', () => {
                const isAdmin = item.textContent.includes('Admin Access');
                const codes = item.querySelectorAll('code');
                
                if (codes.length >= 2) {
                    const username = codes[0].textContent;
                    const password = codes[1].textContent;
                    
                    if (isAdmin) {
                        this.switchToAdmin();
                        setTimeout(() => {
                            document.getElementById('adminUsername').value = username;
                            document.getElementById('adminPassword').value = password;
                        }, 300);
                    } else {
                        this.switchToUser();
                        setTimeout(() => {
                            document.getElementById('userUsername').value = username;
                            document.getElementById('userPassword').value = password;
                        }, 300);
                    }
                    
                    this.showToast('Demo credentials filled!', 'info');
                }
            });
        });
    }

    async handleUserLogin(e) {
        e.preventDefault();
        
        const username = document.getElementById('userUsername').value.trim();
        const password = document.getElementById('userPassword').value;

        if (!username || !password) {
            this.showToast('Please enter both username and password', 'error');
            return;
        }

        this.showLoading('Authenticating user...');

        // Simulate authentication delay
        setTimeout(() => {
            const userAuth = this.authenticateUser(username, password);
            if (userAuth) {
                this.setSession(username, 'user', userAuth.isAdmin);
                const message = userAuth.isAdmin ? 
                    'Admin logged in as user! Redirecting to chat...' : 
                    'Login successful! Redirecting...';
                this.showToast(message, 'success');
                
                setTimeout(() => {
                    window.location.href = 'chat.html';
                }, 1500);
            } else {
                this.hideLoading();
                this.showToast('Invalid username or password', 'error');
                this.shakeForm();
            }
        }, 1500);
    }

    async handleAdminLogin(e) {
        e.preventDefault();
        
        const username = document.getElementById('adminUsername').value.trim();
        const password = document.getElementById('adminPassword').value;

        if (!username || !password) {
            this.showToast('Please enter both username and password', 'error');
            return;
        }

        this.showLoading('Verifying admin credentials...');

        // Simulate authentication delay
        setTimeout(() => {
            if (this.authenticateAdmin(username, password)) {
                this.setSession(username, 'admin');
                this.showToast('Admin login successful! Redirecting...', 'success');
                
                setTimeout(() => {
                    window.location.href = 'index.html'; // Admin dashboard
                }, 1500);
            } else {
                this.hideLoading();
                this.showToast('Invalid admin credentials', 'error');
                this.shakeForm();
            }
        }, 1500);
    }

    authenticateUser(username, password) {
        const user = this.users[username];
        return user && user.password === password ? user : false;
    }

    authenticateAdmin(username, password) {
        const admin = this.admins[username];
        return admin && admin.password === password;
    }

    setSession(username, role, isAdmin = false) {
        const sessionData = {
            username,
            role,
            isAdmin, // Track if this user has admin privileges
            loginTime: new Date().toISOString(),
            expiresAt: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString() // 24 hours
        };
        
        localStorage.setItem('userSession', JSON.stringify(sessionData));
        sessionStorage.setItem('isAuthenticated', 'true');
    }

    checkExistingSession() {
        const session = localStorage.getItem('userSession');
        if (session) {
            try {
                const sessionData = JSON.parse(session);
                const now = new Date();
                const expiresAt = new Date(sessionData.expiresAt);
                
                if (now < expiresAt) {
                    // Valid session exists
                    this.showToast('Welcome back! Redirecting...', 'info');
                    setTimeout(() => {
                        if (sessionData.role === 'admin') {
                            window.location.href = 'index.html';
                        } else {
                            window.location.href = 'chat.html';
                        }
                    }, 1000);
                } else {
                    // Session expired
                    localStorage.removeItem('userSession');
                    sessionStorage.removeItem('isAuthenticated');
                }
            } catch (error) {
                console.error('Error parsing session:', error);
                localStorage.removeItem('userSession');
                sessionStorage.removeItem('isAuthenticated');
            }
        }
    }

    switchToAdmin() {
        const userForm = document.getElementById('userLoginForm');
        const adminForm = document.getElementById('adminLoginForm');
        
        userForm.style.display = 'none';
        adminForm.style.display = 'block';
        adminForm.classList.add('admin-form');
        
        // Focus on admin username field
        setTimeout(() => {
            document.getElementById('adminUsername').focus();
        }, 300);
    }

    switchToUser() {
        const userForm = document.getElementById('userLoginForm');
        const adminForm = document.getElementById('adminLoginForm');
        
        adminForm.style.display = 'none';
        userForm.style.display = 'block';
        adminForm.classList.remove('admin-form');
        
        // Focus on user username field
        setTimeout(() => {
            document.getElementById('userUsername').focus();
        }, 300);
    }

    showLoading(text = 'Loading...') {
        const overlay = document.getElementById('loadingOverlay');
        const loadingText = document.getElementById('loadingText');
        
        if (overlay && loadingText) {
            loadingText.textContent = text;
            overlay.classList.add('show');
        }
    }

    hideLoading() {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.classList.remove('show');
        }
    }

    shakeForm() {
        const activeForm = document.querySelector('.login-form-container:not([style*="display: none"])');
        if (activeForm) {
            activeForm.style.animation = 'shake 0.5s ease-in-out';
            setTimeout(() => {
                activeForm.style.animation = '';
            }, 500);
        }
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
}

// Password toggle functionality
function togglePassword(inputId) {
    const input = document.getElementById(inputId);
    const toggle = input.parentElement.querySelector('.password-toggle i');
    
    if (input.type === 'password') {
        input.type = 'text';
        toggle.className = 'fas fa-eye-slash';
    } else {
        input.type = 'password';
        toggle.className = 'fas fa-eye';
    }
}

// Form switching functions (called from HTML)
function switchToAdmin() {
    if (window.loginSystem) {
        window.loginSystem.switchToAdmin();
    }
}

function switchToUser() {
    if (window.loginSystem) {
        window.loginSystem.switchToUser();
    }
}

// Add shake animation CSS
const shakeCSS = `
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
        20%, 40%, 60%, 80% { transform: translateX(5px); }
    }
`;

const style = document.createElement('style');
style.textContent = shakeCSS;
document.head.appendChild(style);

// Initialize login system when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.loginSystem = new LoginSystem();
});
