// Enhanced Chat functionality with document upload, RAG toggle, and chat history
class ChatInterface {
    constructor() {
        this.apiBase = window.API_BASE || 'http://localhost:8000';
        this.messages = [];
        this.uploadedFiles = [];
        this.sessionFiles = {}; // Store files per session
        this.isTyping = false;
        this.ragMode = false; // Default to Direct mode
        this.knowledgeBaseStats = { documents: 0, chunks: 0 };
        this.wasSetFromDashboard = false;
        this.authChecked = false; // Prevent multiple auth checks
        this.isRedirecting = false; // Prevent redirect loops
        this.currentChatId = 'chat_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        this.chatHistory = [];
        this.init();
    }

    async init() {
        console.log('ChatInterface init starting...');
        
        // Check authentication first - if this fails, it will redirect
        if (!this.checkUserRole()) {
            console.log('Authentication failed, stopping init');
            return; // Stop initialization if not authenticated
        }
        
        console.log('Authentication passed, continuing init...');
        this.setupEventListeners();
        this.setupModeToggle();
        this.setupDocumentUpload();
        this.setupChatHistory();
        this.setupSidebar();
        this.loadChatHistory();
        this.updateModeDisplay(); // This will show the correct mode
        this.updateKnowledgeBaseStatus(); // No loading animation on init
        this.focusInput();
        this.startNewChat(); // Start with a fresh chat
        
        console.log('Chat initialized with mode:', this.ragMode ? 'RAG' : 'Direct');
        
        // Show initial mode message if this was set from dashboard
        if (this.wasSetFromDashboard) {
            setTimeout(() => {
                this.addMessage('assistant', 
                    `🤖 <strong>Mode Set:</strong> You're now in <strong>${this.ragMode ? 'RAG' : 'Direct'} Mode</strong>!<br><br>` +
                    (this.ragMode ? 
                        '📁 Upload documents above to build your knowledge base, then ask me anything about your files!' :
                        '⚡ I\'m ready to chat using my general knowledge. Ask me anything!'
                    ), false, true
                );
            }, 500);
        }
    }

    checkUserRole() {
        // Prevent multiple auth checks
        if (this.authChecked) {
            console.log('Auth already checked, skipping');
            return true;
        }
        
        console.log('Checking user authentication...');
        this.authChecked = true;
        
        // Check user session and role
        const session = localStorage.getItem('userSession');
        const isAuthenticated = sessionStorage.getItem('isAuthenticated');
        
        console.log('Session exists:', !!session);
        console.log('Is authenticated:', isAuthenticated);
        
        if (!session || !isAuthenticated) {
            // Not logged in, redirect to login
            console.log('No session found, redirecting to login');
            window.location.href = 'login.html';
            return false;
        }
        
        try {
            const sessionData = JSON.parse(session);
            const now = new Date();
            const expiresAt = new Date(sessionData.expiresAt);
            
            if (now >= expiresAt) {
                // Session expired, redirect to login
                console.log('Session expired, redirecting to login');
                localStorage.removeItem('userSession');
                sessionStorage.removeItem('isAuthenticated');
                window.location.href = 'login.html';
                return false;
            }
            
            console.log('User authenticated:', sessionData.username, 'Role:', sessionData.role);
            
            // Hide sidebar for regular users, show for admins
            const sidebar = document.getElementById('sidebar');
            const mainContent = document.querySelector('.main-content');
            
            if (sessionData.role === 'user') {
                // Hide sidebar for regular users
                if (sidebar) {
                    sidebar.style.display = 'none';
                }
                // Make main content full width
                if (mainContent) {
                    mainContent.style.marginLeft = '0';
                    mainContent.style.width = '100%';
                }
                
                // Add logout button to chat header for users
                this.addUserLogoutButton(sessionData.username, sessionData.isAdmin);
                
            } else if (sessionData.role === 'admin') {
                // Show sidebar for admins
                if (sidebar) {
                    sidebar.style.display = 'flex';
                }
                if (mainContent) {
                    mainContent.style.marginLeft = '250px';
                    mainContent.style.width = 'calc(100% - 250px)';
                }
            }
            
            return true;
            
        } catch (error) {
            console.error('Error parsing session:', error);
            localStorage.removeItem('userSession');
            sessionStorage.removeItem('isAuthenticated');
            window.location.href = 'login.html';
            return false;
        }
    }

    addUserLogoutButton(username, isAdmin = false) {
        // Add a simple user menu to the chat header for regular users
        const chatHeader = document.querySelector('.chat-header');
        if (chatHeader) {
            const userMenu = document.createElement('div');
            userMenu.className = 'user-menu-simple';
            
            const adminButton = isAdmin ? `
                <button class="admin-access-btn" onclick="switchToAdminPortal()" title="Access Admin Portal">
                    <i class="fas fa-shield-alt"></i>
                </button>
            ` : '';
            
            userMenu.innerHTML = `
                <div class="user-info">
                    <i class="fas fa-user-circle"></i>
                    <span>${username}${isAdmin ? ' (Admin)' : ''}</span>
                </div>
                ${adminButton}
                <button class="logout-btn" onclick="logoutUser()" title="Logout">
                    <i class="fas fa-sign-out-alt"></i>
                </button>
            `;
            chatHeader.appendChild(userMenu);
        }
    }

    setupEventListeners() {
        // Chat input handling
        const chatInput = document.getElementById('chatInput');
        const sendButton = document.getElementById('sendButton');

        if (chatInput) {
            chatInput.addEventListener('keydown', (e) => this.handleKeyDown(e));
            chatInput.addEventListener('input', () => this.handleInputChange());
        }

        if (sendButton) {
            // Remove any existing listeners first
            sendButton.removeEventListener('click', this.sendMessage);
            sendButton.addEventListener('click', () => this.sendMessage());
        }

        // Chat controls
        const clearButton = document.getElementById('clearChat');

        if (clearButton) {
            clearButton.addEventListener('click', () => this.clearChat());
        }

        // Settings panel removed for cleaner interface
    }

    setupModeToggle() {
        const ragModeToggle = document.getElementById('ragModeToggle');
        
        if (ragModeToggle) {
            ragModeToggle.addEventListener('change', (e) => {
                this.ragMode = e.target.checked;
                this.updateModeDisplay();
                this.showModeChangeMessage();
                this.updateKnowledgeBaseStatus(); // No loading animation on mode change
                
                // Save mode preference
                localStorage.setItem('chatRagMode', this.ragMode);
            });
            
            // Check for mode from user dashboard first
            const selectedMode = localStorage.getItem('selectedChatMode');
            console.log('Selected mode from dashboard:', selectedMode);
            
            if (selectedMode) {
                this.ragMode = selectedMode === 'rag';
                ragModeToggle.checked = this.ragMode;
                this.wasSetFromDashboard = true;
                console.log('Setting mode from dashboard:', this.ragMode ? 'RAG' : 'Direct');
                // Clear the selected mode so it doesn't persist
                localStorage.removeItem('selectedChatMode');
            } else {
                // Load saved mode preference (defaults to false/Direct mode)
                const savedMode = localStorage.getItem('chatRagMode');
                this.ragMode = savedMode === 'true'; // Defaults to false (Direct mode)
                ragModeToggle.checked = this.ragMode;
                console.log('Setting mode from saved preference:', this.ragMode ? 'RAG' : 'Direct');
            }
        }
    }

    updateModeDisplay() {
        // Update mode badge
        const modeBadge = document.getElementById('modeBadge');
        if (modeBadge) {
            modeBadge.className = `mode-badge ${this.ragMode ? 'rag-mode' : 'direct-mode'}`;
            modeBadge.innerHTML = this.ragMode ? 
                '<i class="fas fa-folder-open"></i> RAG Mode' : 
                '<i class="fas fa-bolt"></i> Direct Mode';
        }

        // Update mode info panel
        document.querySelectorAll('.mode-info').forEach(info => {
            info.classList.remove('active');
        });
        
        const activeInfo = document.getElementById(this.ragMode ? 'ragModeInfo' : 'directModeInfo');
        if (activeInfo) {
            activeInfo.classList.add('active');
        }

        // Update document upload section visibility
        const uploadSection = document.getElementById('documentUploadSection');
        const compactUploadSection = document.getElementById('compactUploadSection');
        
        if (uploadSection) {
            if (this.ragMode) {
                uploadSection.classList.remove('collapsed');
            } else {
                uploadSection.classList.add('collapsed');
            }
        }
        
        if (compactUploadSection) {
            compactUploadSection.style.display = this.ragMode ? 'block' : 'none';
        }

        // Update welcome message
        const directWelcome = document.querySelector('.direct-welcome');
        const ragWelcome = document.querySelector('.rag-welcome');
        
        if (directWelcome && ragWelcome) {
            if (this.ragMode) {
                directWelcome.style.display = 'none';
                ragWelcome.style.display = 'block';
            } else {
                directWelcome.style.display = 'block';
                ragWelcome.style.display = 'none';
            }
        }

        // Update chat input placeholder
        const chatInput = document.getElementById('chatInput');
        if (chatInput) {
            chatInput.placeholder = this.ragMode ? 
                'Ask me about your uploaded documents... (Shift+Enter for new line)' :
                'Type your message here... (Shift+Enter for new line)';
        }
    }

    showModeChangeMessage() {
        const modeMessage = this.ragMode ? 
            'Switched to RAG Mode! Upload documents to build your knowledge base.' :
            'Switched to Direct Mode! I\'ll use OpenAI\'s general knowledge to assist you.';
        
        this.addMessage('assistant', `🔄 ${modeMessage}`, false, true);
        this.showToast(modeMessage, 'info');
    }

    async updateKnowledgeBaseStatus(showLoading = false) {
        const kbStatusText = document.getElementById('kbStatusText');
        const documentCount = document.getElementById('documentCount');
        const chunkCount = document.getElementById('chunkCount');
        const fileCount = document.getElementById('fileCount');

        try {
            // Only show loading state if explicitly requested
            if (showLoading && kbStatusText) {
                kbStatusText.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading knowledge base status...';
            }

            // Fetch session-specific knowledge base stats from server
            console.log('Fetching KB stats for session:', this.currentChatId);
            const response = await fetch(`${this.apiBase}/knowledge-base/stats?session_id=${this.currentChatId}`);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const stats = await response.json();
            console.log('KB Stats received:', stats);

            if (documentCount) {
                documentCount.textContent = stats.total_documents || 0;
            }

            if (chunkCount) {
                chunkCount.textContent = stats.total_chunks || 0;
            }

            if (fileCount) {
                fileCount.textContent = stats.total_documents || 0;
            }

            if (kbStatusText) {
                if (stats.total_documents === 0) {
                    kbStatusText.textContent = 'No documents uploaded yet. Upload documents to get started with RAG mode.';
                } else {
                    kbStatusText.textContent = `Knowledge base ready with ${stats.total_documents} document(s). Ask me anything about your uploaded content!`;
                }
            }
        } catch (error) {
            console.error('Error fetching knowledge base stats:', error);
            // Show error state with fallback to empty stats
            if (kbStatusText) {
                kbStatusText.textContent = 'No documents uploaded yet. Upload documents to get started with RAG mode.';
            }
            if (documentCount) documentCount.textContent = '0';
            if (chunkCount) chunkCount.textContent = '0';
            if (fileCount) fileCount.textContent = '0';
        }
    }

    setupDocumentUpload() {
        const uploadBtn = document.getElementById('uploadBtn');
        const fileInput = document.getElementById('fileInput');
        const uploadTooltip = document.getElementById('uploadTooltip');
        const compactUploadSection = document.getElementById('compactUploadSection');

        if (uploadBtn && fileInput) {
            // Click to upload
            uploadBtn.addEventListener('click', () => fileInput.click());
            fileInput.addEventListener('change', (e) => this.handleFileSelect(e));
            
            // Tooltip functionality
            if (uploadTooltip) {
                let tooltipTimeout;
                
                uploadBtn.addEventListener('mouseenter', () => {
                    clearTimeout(tooltipTimeout);
                    uploadTooltip.classList.add('show');
                });
                
                uploadBtn.addEventListener('mouseleave', () => {
                    tooltipTimeout = setTimeout(() => {
                        uploadTooltip.classList.remove('show');
                    }, 300);
                });
                
                uploadTooltip.addEventListener('mouseenter', () => {
                    clearTimeout(tooltipTimeout);
                });
                
                uploadTooltip.addEventListener('mouseleave', () => {
                    uploadTooltip.classList.remove('show');
                });
            }
            
            // Drag and drop on the entire compact section
            if (compactUploadSection) {
                compactUploadSection.addEventListener('dragover', (e) => this.handleDragOver(e));
                compactUploadSection.addEventListener('dragleave', (e) => this.handleDragLeave(e));
                compactUploadSection.addEventListener('drop', (e) => this.handleDrop(e));
            }
        }
    }

    handleKeyDown(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            this.sendMessage();
        }
    }

    handleInputChange() {
        const chatInput = document.getElementById('chatInput');
        const sendButton = document.getElementById('sendButton');
        
        if (chatInput && sendButton) {
            sendButton.disabled = !chatInput.value.trim();
        }

        // Auto-resize textarea
        if (chatInput) {
            chatInput.style.height = 'auto';
            chatInput.style.height = Math.min(chatInput.scrollHeight, 120) + 'px';
        }
    }

    async sendMessage() {
        const chatInput = document.getElementById('chatInput');
        const sendButton = document.getElementById('sendButton');
        
        if (!chatInput || !chatInput.value.trim()) return;
        
        // Prevent duplicate requests
        if (this.currentRequest) {
            console.log('Request already in progress, ignoring duplicate');
            return;
        }

        const message = chatInput.value.trim();
        chatInput.value = '';
        chatInput.style.height = '44px';
        sendButton.disabled = true;
        
        // Mark request as in progress and create abort controller
        this.abortController = new AbortController();
        this.currentRequest = true;

        // Change send button to stop button
        this.showStopButton();

        // Add user message to UI (only once)
        this.addMessage('user', message);
        this.showTypingIndicator();

        try {
            // Prepare request data
            const requestData = {
                message: message,
                session_id: this.getSessionId(),
                use_rag: this.ragMode
            };

            // Include uploaded files if in RAG mode and files are available
            if (this.ragMode && this.uploadedFiles.length > 0) {
                requestData.uploaded_files = this.uploadedFiles.map(file => ({
                    name: file.name,
                    content: file.content,
                    type: file.type
                }));
            }

            // Show mode-specific guidance if needed
            if (this.ragMode && this.uploadedFiles.length === 0) {
                this.showToast('Upload documents first to use RAG mode effectively!', 'warning');
            }

            const response = await fetch(`${this.apiBase}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestData),
                signal: this.abortController.signal
            });

            this.hideTypingIndicator();

            if (response.ok) {
                const data = await response.json();
                this.addMessage('assistant', data.response);
                
                // Update chat info
                this.updateChatInfo(data);
            } else {
                const errorData = await response.json();
                this.addMessage('assistant', `Error: ${errorData.detail || 'Something went wrong'}`, true);
            }
        } catch (error) {
            this.hideTypingIndicator();
            
            // Check if the request was aborted (user clicked stop)
            if (error.name === 'AbortError') {
                console.log('Request was aborted by user');
                return; // Don't show error message for intentional stops
            }
            
            this.addMessage('assistant', 'Sorry, I encountered an error. Please try again.', true);
            console.error('Chat error:', error);
        } finally {
            // Clear request flag and abort controller
            this.currentRequest = null;
            this.abortController = null;
            this.hideStopButton();
            sendButton.disabled = false;
            this.focusInput();
        }
    }

    showStopButton() {
        const sendButton = document.getElementById('sendButton');
        if (sendButton) {
            sendButton.innerHTML = '<i class="fas fa-stop"></i>';
            sendButton.className = 'send-button stop-button';
            sendButton.disabled = false;
            sendButton.title = 'Stop generation';
            
            // Remove old event listener and add stop functionality
            sendButton.removeEventListener('click', this.sendMessage);
            sendButton.addEventListener('click', () => this.stopGeneration());
        }
    }

    hideStopButton() {
        const sendButton = document.getElementById('sendButton');
        if (sendButton) {
            sendButton.innerHTML = '<i class="fas fa-paper-plane"></i>';
            sendButton.className = 'send-button';
            sendButton.title = 'Send message';
            
            // Remove stop listener and restore send functionality
            sendButton.removeEventListener('click', this.stopGeneration);
            sendButton.addEventListener('click', () => this.sendMessage());
        }
    }

    stopGeneration() {
        if (this.currentRequest && this.abortController) {
            // Abort the current fetch request
            this.abortController.abort();
            
            // Cancel the current request
            this.currentRequest = null;
            
            // Hide typing indicator
            this.hideTypingIndicator();
            
            // Add a message indicating the generation was stopped
            this.addMessage('assistant', '⏹️ Generation stopped by user.', false, true);
            
            // Reset button state
            this.hideStopButton();
            
            const sendButton = document.getElementById('sendButton');
            if (sendButton) {
                sendButton.disabled = false;
            }
            
            console.log('Generation stopped by user');
        }
    }

    formatAIResponse(text) {
        // Convert common formatting patterns to HTML
        let formatted = text
            // Convert bullet points
            .replace(/^\s*[\*\-\+]\s+(.+)$/gm, '<li>$1</li>')
            // Convert numbered lists
            .replace(/^\s*\d+\.\s+(.+)$/gm, '<li>$1</li>')
            // Convert **bold** to <strong>
            .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
            // Convert *italic* to <em>
            .replace(/\*(.+?)\*/g, '<em>$1</em>')
            // Convert line breaks to <br>
            .replace(/\n/g, '<br>');
        
        // Wrap consecutive <li> elements in <ul>
        formatted = formatted.replace(/(<li>.*<\/li>)(\s*<br>\s*<li>.*<\/li>)*/g, function(match) {
            return '<ul>' + match.replace(/<br>\s*/g, '') + '</ul>';
        });
        
        return formatted;
    }

    addMessage(sender, text, isError = false, isSystem = false) {
        // Display the message
        this.displayMessage(sender, text, isError, isSystem);

        // Store message (don't store system messages in history)
        if (!isSystem) {
            this.messages.push({
                type: sender,
                content: text,
                timestamp: Date.now(),
                isError
            });

            // Auto-save chat after each message with debouncing
            if (this.currentChatId) {
                clearTimeout(this.saveTimeout);
                this.saveTimeout = setTimeout(() => {
                    this.saveCurrentChat();
                    this.renderChatHistory();
                }, 1000);
            }
        }
    }

    displayMessage(sender, text, isError = false, isSystem = false) {
        const messagesContainer = document.getElementById('chatMessages');
        if (!messagesContainer) return;

        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        if (isSystem) messageDiv.classList.add('system-message');
        
        const avatarDiv = document.createElement('div');
        avatarDiv.className = 'message-avatar';
        if (isSystem) {
            avatarDiv.innerHTML = '<i class="fas fa-cog"></i>';
        } else {
            avatarDiv.innerHTML = sender === 'user' ? '<i class="fas fa-user"></i>' : '<i class="fas fa-robot"></i>';
        }

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        if (isError) contentDiv.classList.add('error');
        if (isSystem) contentDiv.classList.add('system');

        const textDiv = document.createElement('div');
        textDiv.className = 'message-text';
        
        // Preserve formatting for AI responses
        if (sender === 'assistant' && !isSystem) {
            textDiv.innerHTML = this.formatAIResponse(text);
        } else {
            textDiv.innerHTML = text; // Allow HTML for system messages
        }

        const timeDiv = document.createElement('div');
        timeDiv.className = 'message-time';
        timeDiv.textContent = new Date().toLocaleTimeString();

        contentDiv.appendChild(textDiv);
        contentDiv.appendChild(timeDiv);
        messageDiv.appendChild(avatarDiv);
        messageDiv.appendChild(contentDiv);

        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    showTypingIndicator() {
        if (this.isTyping) return;
        
        const messagesContainer = document.getElementById('chatMessages');
        const typingIndicator = document.getElementById('typingIndicator');
        
        if (typingIndicator) {
            typingIndicator.style.display = 'flex';
            this.isTyping = true;
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
    }

    hideTypingIndicator() {
        const typingIndicator = document.getElementById('typingIndicator');
        if (typingIndicator) {
            typingIndicator.style.display = 'none';
            this.isTyping = false;
        }
    }

    // Document Upload Functions
    handleDragOver(e) {
        e.preventDefault();
        e.stopPropagation();
        const compactSection = document.getElementById('compactUploadSection');
        if (compactSection) {
            compactSection.classList.add('drag-over');
        }
    }

    handleDragLeave(e) {
        e.preventDefault();
        e.stopPropagation();
        const compactSection = document.getElementById('compactUploadSection');
        if (compactSection) {
            compactSection.classList.remove('drag-over');
        }
    }

    handleDrop(e) {
        e.preventDefault();
        e.stopPropagation();
        const compactSection = document.getElementById('compactUploadSection');
        if (compactSection) {
            compactSection.classList.remove('drag-over');
        }
        
        const files = Array.from(e.dataTransfer.files);
        this.processFiles(files);
    }

    handleFileSelect(e) {
        const files = Array.from(e.target.files);
        this.processFiles(files);
        e.target.value = ''; // Reset input
    }

    async processFiles(files) {
        const allowedTypes = [
            'text/plain', 'application/pdf', 'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'text/csv', 'application/json'
        ];

        let successCount = 0;
        let errorCount = 0;

        for (const file of files) {
            if (!allowedTypes.includes(file.type)) {
                this.showToast(`File type not supported: ${file.name}`, 'error');
                errorCount++;
                continue;
            }

            if (file.size > 10 * 1024 * 1024) { // 10MB limit
                this.showToast(`File too large: ${file.name} (max 10MB)`, 'error');
                errorCount++;
                continue;
            }

            try {
                // Show loading state
                this.showUploadingState(file.name);
                
                // Upload file to server
                await this.uploadFileToServer(file);
                
                const content = await this.readFileContent(file);
                const uploadedFile = {
                    name: file.name,
                    size: file.size,
                    type: file.type,
                    content: content,
                    id: Date.now() + Math.random() + Math.random() * 1000 + successCount
                };

                // Store file in session-specific array
                if (!this.sessionFiles[this.currentChatId]) {
                    this.sessionFiles[this.currentChatId] = [];
                }
                this.sessionFiles[this.currentChatId].push(uploadedFile);
                
                successCount++;
                this.showToast(`File uploaded: ${file.name}`, 'success');
            } catch (error) {
                errorCount++;
                this.showToast(`Error uploading file: ${file.name} - ${error.message}`, 'error');
                console.error('File upload error:', error);
            }
        }

        // Update UI once after all files are processed
        if (successCount > 0) {
            // Update current session's uploaded files
            this.uploadedFiles = this.sessionFiles[this.currentChatId];
            this.updateUploadedFilesList();
            
            // Update knowledge base status
            await this.updateKnowledgeBaseStatus(false);
            
            if (successCount > 1) {
                this.showToast(`${successCount} files uploaded successfully!`, 'success');
            }
        }

        // Hide loading state
        this.hideUploadingState();
    }

    async uploadFileToServer(file) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('initialize_kb', 'true'); // Initialize knowledge base after upload
        formData.append('session_id', this.currentChatId); // Use current chat ID as session ID
        
        const response = await fetch('http://localhost:8000/upload-document', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.message || `Upload failed: ${response.status}`);
        }
        
        const result = await response.json();
        if (!result.success) {
            throw new Error(result.message || 'Upload failed');
        }
        
        return result;
    }

    readFileContent(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (e) => resolve(e.target.result);
            reader.onerror = reject;
            reader.readAsText(file);
        });
    }

    updateUploadedFilesList() {
        // Update both the old list (if exists) and new compact preview
        this.updateFileChips();
        
        const uploadedFilesList = document.getElementById('uploadedFilesList');
        if (uploadedFilesList) {
            if (this.uploadedFiles.length === 0) {
                uploadedFilesList.classList.remove('has-files');
                return;
            }

            uploadedFilesList.classList.add('has-files');
            uploadedFilesList.innerHTML = this.uploadedFiles.map(file => `
                <div class="file-item" data-file-id="${file.id}">
                    <div class="file-info">
                        <i class="fas fa-file-alt file-icon"></i>
                        <div>
                            <div class="file-name">${file.name}</div>
                            <div class="file-size">${this.formatFileSize(file.size)}</div>
                        </div>
                    </div>
                    <div class="file-actions">
                        <button class="file-remove" onclick="chatInterface.removeFile(${file.id})">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                </div>
            `).join('');
        }
    }

    updateFileChips() {
        const filesPreview = document.getElementById('filesPreview');
        if (!filesPreview) return;

        if (this.uploadedFiles.length === 0) {
            filesPreview.innerHTML = '';
            return;
        }

        filesPreview.innerHTML = this.uploadedFiles.map(file => `
            <div class="file-chip" data-file-id="${file.id}">
                <i class="fas fa-file-alt"></i>
                <span class="file-chip-name" title="${file.name}">${file.name}</span>
                <button class="file-chip-remove" onclick="chatInterface.removeFile(${file.id})" title="Remove file">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `).join('');
    }

    removeFile(fileId) {
        // Remove from session-specific files
        if (this.sessionFiles[this.currentChatId]) {
            this.sessionFiles[this.currentChatId] = this.sessionFiles[this.currentChatId].filter(file => file.id !== fileId);
        }
        
        // Update current session's uploaded files
        this.uploadedFiles = this.sessionFiles[this.currentChatId] || [];
        this.updateUploadedFilesList();
        this.updateKnowledgeBaseStatus(true); // Show loading when removing file
        this.showToast('File removed', 'info');
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    // UI Helper Functions
    toggleUploadSection() {
        const uploadSection = document.getElementById('documentUploadSection');
        if (uploadSection) {
            uploadSection.classList.toggle('collapsed');
        }
    }

    // Settings functionality removed for cleaner interface
    
    showUploadingState(fileName) {
        const kbStatusText = document.getElementById('kbStatusText');
        if (kbStatusText) {
            kbStatusText.innerHTML = `
                <i class="fas fa-spinner fa-spin"></i> 
                Uploading and processing "${fileName}"...
            `;
        }
        
        // Show loading in document count
        const documentCount = document.getElementById('documentCount');
        if (documentCount) {
            documentCount.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
        }
    }
    
    hideUploadingState() {
        // Update knowledge base status without loading animation
        this.updateKnowledgeBaseStatus(false);
    }

    clearChat() {
        if (confirm('Are you sure you want to clear all messages?')) {
            const messagesContainer = document.getElementById('chatMessages');
            if (messagesContainer) {
                messagesContainer.innerHTML = '';
            }
            this.messages = [];
            this.uploadedFiles = [];
            this.updateUploadedFilesList();
            localStorage.removeItem('chatHistory');
            this.showToast('Chat cleared', 'info');
        }
    }

    exportChat() {
        const data = {
            messages: this.messages,
            exportDate: new Date().toISOString(),
            sessionId: this.getSessionId()
        };

        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `chat-export-${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        this.showToast('Chat exported', 'success');
    }

    // Utility Functions
    getSessionId() {
        // Use current chat ID as session ID for isolated knowledge bases
        return this.currentChatId || 'default_session';
    }

    saveChatHistory() {
        localStorage.setItem('chatHistory', JSON.stringify(this.messages));
    }

    loadChatHistory() {
        const history = localStorage.getItem('chatHistory');
        if (history) {
            try {
                this.messages = JSON.parse(history);
                this.renderChatHistory();
            } catch (error) {
                console.error('Error loading chat history:', error);
            }
        }
    }

    renderChatHistory() {
        const messagesContainer = document.getElementById('chatMessages');
        if (!messagesContainer) return;

        messagesContainer.innerHTML = '';
        this.messages.forEach(msg => {
            this.addMessageToDOM(msg.sender, msg.text, msg.isError, msg.timestamp);
        });
    }

    addMessageToDOM(sender, text, isError = false, timestamp = null) {
        const messagesContainer = document.getElementById('chatMessages');
        if (!messagesContainer) return;

        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        
        const avatarDiv = document.createElement('div');
        avatarDiv.className = 'message-avatar';
        avatarDiv.innerHTML = sender === 'user' ? '<i class="fas fa-user"></i>' : '<i class="fas fa-robot"></i>';

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        if (isError) contentDiv.classList.add('error');

        const textDiv = document.createElement('div');
        textDiv.className = 'message-text';
        textDiv.textContent = text;

        const timeDiv = document.createElement('div');
        timeDiv.className = 'message-time';
        timeDiv.textContent = timestamp ? 
            new Date(timestamp).toLocaleTimeString() : 
            new Date().toLocaleTimeString();

        contentDiv.appendChild(textDiv);
        contentDiv.appendChild(timeDiv);
        messageDiv.appendChild(avatarDiv);
        messageDiv.appendChild(contentDiv);

        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    updateChatInfo(data) {
        // Update chat statistics if available
        if (data.metrics) {
            const responseTime = document.querySelector('.response-time');
            const tokenCount = document.querySelector('.token-count');
            const cost = document.querySelector('.session-cost');

            if (responseTime) responseTime.textContent = `${data.metrics.response_time}ms`;
            if (tokenCount) tokenCount.textContent = data.metrics.tokens_used || 0;
            if (cost) cost.textContent = `$${(data.metrics.cost || 0).toFixed(4)}`;
        }
    }

    focusInput() {
        const chatInput = document.getElementById('chatInput');
        if (chatInput) {
            setTimeout(() => chatInput.focus(), 100);
        }
    }

    showToast(message, type = 'info') {
        // Create toast notification
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check' : type === 'error' ? 'exclamation-triangle' : 'info-circle'}"></i>
            <span>${message}</span>
        `;

        document.body.appendChild(toast);

        // Auto remove after 3 seconds
        setTimeout(() => {
            toast.style.animation = 'slideOutRight 0.3s ease forwards';
            setTimeout(() => document.body.removeChild(toast), 300);
        }, 3000);
    }

    // Chat History Management
    setupChatHistory() {
        // Load chat history from localStorage
        this.chatHistory = JSON.parse(localStorage.getItem('chatHistory') || '[]');
        
        // Setup event listeners
        const newChatBtn = document.getElementById('newChatBtn');
        const clearAllBtn = document.getElementById('clearAllChats');
        const chatSearchInput = document.getElementById('chatSearchInput');
        
        if (newChatBtn) {
            newChatBtn.addEventListener('click', () => this.startNewChat());
        }
        
        if (clearAllBtn) {
            clearAllBtn.addEventListener('click', () => this.clearAllChats());
        }
        
        if (chatSearchInput) {
            chatSearchInput.addEventListener('input', (e) => this.searchChats(e.target.value));
        }
        
        this.renderChatHistory();
    }
    
    startNewChat() {
        // Save current chat if it has valid messages
        if (this.messages && this.messages.length > 0) {
            const hasValidMessages = this.messages.some(msg => 
                msg && msg.content && msg.content.trim() && msg.content.trim() !== ''
            );
            if (hasValidMessages) {
                this.saveCurrentChat();
            }
        }
        
        // Create new chat with unique ID
        this.currentChatId = 'chat_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        this.messages = [];
        
        // Load uploaded files for this session (or empty array for new session)
        this.uploadedFiles = this.sessionFiles[this.currentChatId] || [];
        this.updateUploadedFilesList();
        
        // Reset any pending requests
        if (this.currentRequest) {
            this.currentRequest = null;
        }
        
        this.clearChatMessages();
        this.showWelcomeMessage();
        this.renderChatHistory();
        
        // Update knowledge base status for new session
        this.updateKnowledgeBaseStatus(false);
        
        console.log('Started new chat:', this.currentChatId);
    }
    
    loadChatSession(chatId) {
        // Switch to existing chat session
        console.log('Switching from session:', this.currentChatId, 'to session:', chatId);
        this.currentChatId = chatId;
        
        // Load uploaded files for this session
        this.uploadedFiles = this.sessionFiles[this.currentChatId] || [];
        this.updateUploadedFilesList();
        
        // Update knowledge base status for this session
        this.updateKnowledgeBaseStatus(false);
        
        console.log('Loaded chat session:', this.currentChatId, 'with', this.uploadedFiles.length, 'files');
        console.log('Session files:', this.sessionFiles);
    }
    
    saveCurrentChat() {
        if (!this.currentChatId || this.messages.length === 0) return;
        
        const chatData = {
            id: this.currentChatId,
            title: this.generateChatTitle(),
            messages: [...this.messages],
            timestamp: Date.now(),
            mode: this.ragMode ? 'RAG' : 'Direct'
        };
        
        // Remove existing chat with same ID
        this.chatHistory = this.chatHistory.filter(chat => chat.id !== this.currentChatId);
        
        // Add to beginning of history
        this.chatHistory.unshift(chatData);
        
        // Keep only last 50 chats
        if (this.chatHistory.length > 50) {
            this.chatHistory = this.chatHistory.slice(0, 50);
        }
        
        // Save to localStorage
        localStorage.setItem('chatHistory', JSON.stringify(this.chatHistory));
        
        console.log('Saved chat:', chatData.title);
    }
    
    loadChat(chatId) {
        const chat = this.chatHistory.find(c => c.id === chatId);
        if (!chat) return;
        
        // Save current chat first
        if (this.messages.length > 0 && this.currentChatId !== chatId) {
            this.saveCurrentChat();
        }
        
        // Load selected chat and switch session context
        this.loadChatSession(chatId);
        this.messages = [...chat.messages];
        this.ragMode = chat.mode === 'RAG';
        
        // Update UI
        this.clearChatMessages();
        this.messages.forEach(msg => {
            this.displayMessage(msg.type, msg.content, msg.isError || false, false);
        });
        
        this.updateModeDisplay();
        this.renderChatHistory();
        
        console.log('Loaded chat:', chat.title);
    }
    
    generateChatTitle() {
        if (!this.messages || this.messages.length === 0) return 'New Chat';
        
        // Find first user message with valid content
        const firstUserMessage = this.messages.find(msg => 
            msg && msg.type === 'user' && msg.content && msg.content.trim()
        );
        
        if (firstUserMessage && firstUserMessage.content) {
            let title = firstUserMessage.content.replace(/<[^>]*>/g, '').trim();
            if (!title || title === '') return 'New Chat';
            return title.length > 50 ? title.substring(0, 50) + '...' : title;
        }
        
        return 'New Chat';
    }
    
    renderChatHistory() {
        const chatList = document.getElementById('chatList');
        if (!chatList) return;
        
        // No sample data - start with empty history
        
        if (this.chatHistory.length === 0) {
            chatList.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-comments"></i>
                    <p>No chat history yet</p>
                    <small>Start a conversation to see it here</small>
                </div>
            `;
            return;
        }
        
        chatList.innerHTML = this.chatHistory.map(chat => {
            const isActive = chat.id === this.currentChatId;
            
            return `
                <div class="chat-item ${isActive ? 'active' : ''}" onclick="chatInterface.loadChat('${chat.id}')">
                    <div class="chat-item-title">${chat.title}</div>
                </div>
            `;
        }).join('');
        
        // Update chat stats
        this.updateChatStats();
    }
    
    updateChatStats() {
        const totalChatsEl = document.getElementById('totalChats');
        const todayChatsEl = document.getElementById('todayChats');
        
        if (totalChatsEl) {
            totalChatsEl.textContent = this.chatHistory.length;
        }
        
        if (todayChatsEl) {
            const today = new Date();
            today.setHours(0, 0, 0, 0);
            const todayChats = this.chatHistory.filter(chat => 
                new Date(chat.timestamp) >= today
            ).length;
            todayChatsEl.textContent = todayChats;
        }
    }
    
    // Sample chat history removed - users start with clean slate
    
    getChatPreview(chat) {
        const lastMessage = chat.messages[chat.messages.length - 1];
        if (!lastMessage) return 'Empty chat';
        
        let preview = lastMessage.content.replace(/<[^>]*>/g, '').trim();
        return preview.length > 100 ? preview.substring(0, 100) + '...' : preview;
    }
    
    getTimeAgo(timestamp) {
        const now = Date.now();
        const diff = now - timestamp;
        const minutes = Math.floor(diff / 60000);
        const hours = Math.floor(diff / 3600000);
        const days = Math.floor(diff / 86400000);
        
        if (minutes < 1) return 'Just now';
        if (minutes < 60) return `${minutes}m ago`;
        if (hours < 24) return `${hours}h ago`;
        if (days < 7) return `${days}d ago`;
        return new Date(timestamp).toLocaleDateString();
    }
    
    searchChats(query) {
        if (!query.trim()) {
            this.renderChatHistory();
            return;
        }
        
        const filtered = this.chatHistory.filter(chat => 
            chat.title.toLowerCase().includes(query.toLowerCase()) ||
            chat.messages.some(msg => 
                msg.content.toLowerCase().includes(query.toLowerCase())
            )
        );
        
        const chatList = document.getElementById('chatList');
        if (!chatList) return;
        
        if (filtered.length === 0) {
            chatList.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-search"></i>
                    <p>No chats found</p>
                    <small>Try a different search term</small>
                </div>
            `;
            return;
        }
        
        chatList.innerHTML = filtered.map(chat => {
            const isActive = chat.id === this.currentChatId;
            
            return `
                <div class="chat-item ${isActive ? 'active' : ''}" onclick="chatInterface.loadChat('${chat.id}')">
                    <div class="chat-item-title">${chat.title}</div>
                </div>
            `;
        }).join('');
    }
    
    clearAllChats() {
        if (confirm('Are you sure you want to clear all chat history? This action cannot be undone.')) {
            this.chatHistory = [];
            localStorage.removeItem('chatHistory');
            this.renderChatHistory();
            console.log('Cleared all chat history');
        }
    }
    
    showWelcomeMessage() {
        const welcomeMessage = `
            <strong>Welcome to GenAI Chatbot!</strong><br><br>
            <span class="mode-welcome">
                I'm running in <strong>${this.ragMode ? 'RAG' : 'Direct'} Mode</strong> - ${this.ragMode ? 
                    'ready to use your custom knowledge base!' : 
                    'ready to chat using OpenAI\'s powerful GPT model!'}<br><br>
                ${this.ragMode ? 
                    '📁 Upload documents above to build your knowledge base, then ask me anything!' :
                    '💡 Switch to RAG Mode above to upload documents for more specialized assistance!'
                }
            </span>
        `;
        
        this.addMessage('assistant', welcomeMessage, false, true);
    }
    
    clearChatMessages() {
        const chatMessages = document.getElementById('chatMessages');
        if (chatMessages) {
            chatMessages.innerHTML = '';
        }
    }
    
    setupSidebar() {
        console.log('Setting up sidebar...'); // Debug log
        
        // Wait for DOM to be fully loaded
        setTimeout(() => {
            console.log('DOM elements check:');
            console.log('sidebarToggle element:', document.getElementById('sidebarToggle'));
            console.log('sidebar element:', document.getElementById('sidebar'));
            const sidebarToggle = document.getElementById('sidebarToggle');
            const externalToggle = document.getElementById('externalToggle');
            const sidebar = document.getElementById('sidebar');
            const mainContent = document.querySelector('.main-content');
            
            console.log('Elements found:', {
                sidebarToggle: !!sidebarToggle,
                externalToggle: !!externalToggle,
                sidebar: !!sidebar,
                mainContent: !!mainContent
            });
            
            const toggleSidebar = () => {
                console.log('Toggle sidebar clicked'); // Debug log
                
                if (!sidebar) {
                    console.error('Sidebar element not found');
                    return;
                }
                
                sidebar.classList.toggle('collapsed');
                
                // Show/hide external toggle button
                const isCollapsed = sidebar.classList.contains('collapsed');
                console.log('Sidebar collapsed:', isCollapsed); // Debug log
                
                if (externalToggle) {
                    externalToggle.style.display = isCollapsed ? 'flex' : 'none';
                }
                
                // Adjust main content margin with !important override
                if (mainContent) {
                    if (isCollapsed) {
                        mainContent.style.setProperty('margin-left', '60px', 'important');
                    } else {
                        mainContent.style.setProperty('margin-left', '260px', 'important');
                    }
                }
                
                // Save sidebar state
                localStorage.setItem('sidebarCollapsed', isCollapsed);
            };
            
            if (sidebarToggle) {
                console.log('Setting up internal toggle'); // Debug log
                sidebarToggle.addEventListener('click', (e) => {
                    console.log('Internal toggle clicked'); // Debug log
                    e.preventDefault();
                    e.stopPropagation();
                    toggleSidebar();
                });
            } else {
                console.error('Sidebar toggle button not found');
            }
            
            if (externalToggle) {
                console.log('Setting up external toggle'); // Debug log
                externalToggle.addEventListener('click', (e) => {
                    console.log('External toggle clicked'); // Debug log
                    e.preventDefault();
                    e.stopPropagation();
                    toggleSidebar();
                });
            }
            
            // Restore sidebar state
            const savedState = localStorage.getItem('sidebarCollapsed');
            if (savedState === 'true' && sidebar) {
                console.log('Restoring collapsed state'); // Debug log
                sidebar.classList.add('collapsed');
                if (externalToggle) {
                    externalToggle.style.display = 'flex';
                }
                if (mainContent) {
                    mainContent.style.setProperty('margin-left', '60px', 'important');
                }
            }
        }, 100); // Small delay to ensure DOM is ready
    }
}

// Global logout function
function logoutUser() {
    // Clear session data
    localStorage.removeItem('userSession');
    sessionStorage.removeItem('isAuthenticated');
    
    // Redirect to login
    window.location.href = 'login.html';
}

// Global function to switch to admin portal
function switchToAdminPortal() {
    const session = localStorage.getItem('userSession');
    if (session) {
        try {
            const sessionData = JSON.parse(session);
            if (sessionData.isAdmin) {
                // Restore admin role and clear user view flag
                sessionData.role = 'admin';
                delete sessionData.currentView; // Remove user view flag
                localStorage.setItem('userSession', JSON.stringify(sessionData));
                // Redirect to admin dashboard
                window.location.href = 'index.html';
            }
        } catch (error) {
            console.error('Error switching to admin portal:', error);
        }
    }
}

// Global flags to prevent multiple initializations and redirect loops
window.chatInterfaceInitialized = window.chatInterfaceInitialized || false;
window.isRedirectingToLogin = window.isRedirectingToLogin || false;

// Initialize chat interface when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Prevent multiple initializations
    if (window.chatInterfaceInitialized || window.chatInterface) {
        console.log('ChatInterface already initialized, skipping');
        return;
    }
    
    console.log('Initializing ChatInterface...');
    window.chatInterfaceInitialized = true;
    window.chatInterface = new ChatInterface();
});

// Export for global access
window.ChatInterface = ChatInterface;
