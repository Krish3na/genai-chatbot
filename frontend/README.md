# GenAI Chatbot Frontend

A modern, responsive web interface for the GenAI Chatbot with comprehensive monitoring and alert management.

## 🚀 Features

### 📊 **Dashboard**
- System health overview
- Real-time statistics
- Recent activity feed
- Quick access to all features

### 💬 **Chat Interface**
- Clean, modern chat UI
- Real-time messaging
- Message history
- Chat statistics
- Export functionality

### 🚨 **Alerts & Monitoring** ⭐
- **Real-time alert dashboard**
- **14 configurable thresholds**
- **Email notification system**
- **Alert filtering and history**
- **Threshold management**
- **System health monitoring**

### 📈 **MLflow Integration**
- Direct access to MLflow UI
- Experiment tracking
- Model performance monitoring

### ⚙️ **Settings**
- Configuration management
- User preferences
- System settings

## 🏗️ Architecture

```
frontend/
├── index.html          # Dashboard page
├── chat.html           # Chat interface
├── alerts.html         # Alerts & monitoring ⭐
├── mlflow.html         # MLflow integration
├── settings.html       # Settings page
├── styles/
│   ├── main.css        # Global styles
│   ├── dashboard.css   # Dashboard styles
│   ├── alerts.css      # Alerts page styles ⭐
│   └── chat.css        # Chat interface styles
└── js/
    ├── main.js         # Core functionality
    ├── alerts.js       # Alerts page logic ⭐
    ├── chat.js         # Chat functionality
    └── dashboard.js    # Dashboard logic
```

## 🎨 Design System

### **Color Palette**
- **Primary**: `#667eea` (Soft Blue)
- **Secondary**: `#764ba2` (Purple)
- **Success**: `#48bb78` (Green)
- **Warning**: `#ed8936` (Orange)
- **Danger**: `#f56565` (Red)
- **Info**: `#4299e1` (Blue)

### **Typography**
- **Font**: System fonts (-apple-system, BlinkMacSystemFont, Segoe UI, Roboto)
- **Responsive sizing**: 12px - 30px
- **Weight**: 400, 500, 600, 700

### **Layout**
- **Sidebar Navigation**: Collapsible, responsive
- **Grid System**: CSS Grid with auto-fit
- **Spacing**: 8px base unit (0.25rem - 3rem)
- **Border Radius**: 8px standard, 12px for cards

## 🚨 **Alerts System Features**

### **Status Overview**
- **System Health**: Real-time status monitoring
- **Alert Counts**: Total, Critical, Warning categorization
- **Email Status**: Configuration and delivery status

### **Alert Management**
- **Real-time Updates**: Auto-refresh every 30 seconds
- **Filtering**: All, Critical, Warning views
- **Detailed Information**: Timestamps, values, thresholds
- **Visual Indicators**: Color-coded severity levels

### **Threshold Configuration**
- **Performance**: Response time monitoring
- **Quality**: Model accuracy tracking
- **Cost**: Daily and per-interaction limits
- **Error Rates**: System reliability monitoring

### **Email Integration**
- **Status Monitoring**: Configuration verification
- **Test Functionality**: Send test alerts
- **Multi-recipient**: Support for multiple email addresses
- **Setup Guide**: Integrated documentation

## 📱 Responsive Design

### **Breakpoints**
- **Desktop**: > 768px (Full sidebar, grid layouts)
- **Tablet**: 481px - 768px (Collapsible sidebar)
- **Mobile**: ≤ 480px (Stacked layouts, touch-optimized)

### **Mobile Features**
- **Touch-friendly**: Large buttons, easy navigation
- **Collapsible Sidebar**: Space-efficient navigation
- **Optimized Layouts**: Single-column on small screens
- **Readable Text**: Appropriate font sizes

## 🔧 API Integration

### **Endpoints Used**
```javascript
// System Health
GET /health
GET /alerts/status

// Alerts Management
GET /alerts/check
GET /alerts/thresholds
POST /alerts/thresholds
GET /alerts/email-config
POST /alerts/test-email

// Chat System
POST /chat
GET /chat/history

// MLflow Integration
GET /mlflow/experiments
GET /mlflow/best-run
```

### **Error Handling**
- **Retry Logic**: Automatic retry with exponential backoff
- **User Feedback**: Toast notifications for all actions
- **Graceful Degradation**: Fallback UI states
- **Connection Status**: Real-time connectivity monitoring

## 🚀 Quick Start

### **1. Setup Backend**
Ensure your GenAI Chatbot backend is running with the alerts system:
```bash
# Start the backend API
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# Start MLflow server
mlflow server --host 0.0.0.0 --port 5000
```

### **2. Serve Frontend**
Option A - Simple HTTP Server:
```bash
cd frontend
python -m http.server 3000
```

Option B - Node.js Server:
```bash
cd frontend
npx serve -p 3000
```

### **3. Access Application**
- **Main App**: http://localhost:3000
- **Alerts Dashboard**: http://localhost:3000/alerts.html
- **Chat Interface**: http://localhost:3000/chat.html

## 🔧 Configuration

### **API Configuration**
Update `CONFIG` in `js/main.js`:
```javascript
const CONFIG = {
    API_BASE_URL: 'http://localhost:8000',
    REFRESH_INTERVAL: 30000,
    MAX_RETRIES: 3,
    RETRY_DELAY: 1000
};
```

### **Email Alerts**
Configure email notifications by:
1. Setting up Gmail App Password
2. Using the built-in configuration interface
3. Testing with the "Test Email" functionality

## 🎯 Key Features Highlights

### **🚨 Advanced Alert System**
- **14 Smart Thresholds**: Performance, quality, cost monitoring
- **Real-time Notifications**: Instant email alerts
- **Visual Dashboard**: Beautiful, intuitive interface
- **Configurable Rules**: Customizable alert conditions
- **History Tracking**: Complete alert audit trail

### **📊 Professional UI**
- **Modern Design**: Clean, professional interface
- **Responsive Layout**: Works on all devices
- **Intuitive Navigation**: Easy-to-use sidebar
- **Real-time Updates**: Live data refresh
- **Accessibility**: WCAG compliant design

### **🔧 Developer-Friendly**
- **Vanilla JavaScript**: No framework dependencies
- **Modular Code**: Easy to extend and maintain
- **Error Handling**: Comprehensive error management
- **API Integration**: RESTful API consumption
- **Documentation**: Well-documented codebase

## 🤝 Integration with Backend

This frontend is specifically designed to work with your GenAI Chatbot backend that includes:
- ✅ **MLflow Integration**: Experiment tracking
- ✅ **Alert System**: 14 configurable thresholds
- ✅ **Email Notifications**: SMTP integration
- ✅ **Prometheus Metrics**: System monitoring
- ✅ **FastAPI Endpoints**: RESTful API

## 🎉 Result

You now have a **complete, professional web application** with:
- **Beautiful UI**: Modern, responsive design
- **Full Functionality**: All features implemented
- **Real-time Monitoring**: Live alerts and status
- **Email Integration**: Automated notifications
- **Mobile Support**: Works on all devices
- **Production Ready**: Professional-grade interface

This frontend transforms your GenAI Chatbot into a **complete web application** suitable for production use! 🚀
