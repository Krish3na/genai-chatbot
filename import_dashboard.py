#!/usr/bin/env python3
"""
Script to help import Grafana dashboard manually
"""
import json
import requests

def import_dashboard():
    """Import the GenAI Chatbot dashboard to Grafana"""
    
    # Grafana connection details
    GRAFANA_URL = "http://localhost:3000"
    USERNAME = "admin"
    PASSWORD = "admin"
    
    # Dashboard JSON
    dashboard_json = {
        "dashboard": {
            "id": None,
            "title": "GenAI Chatbot Dashboard",
            "tags": ["genai", "chatbot", "monitoring"],
            "style": "dark",
            "timezone": "browser",
            "panels": [
                {
                    "id": 1,
                    "title": "Chat Requests Total",
                    "type": "stat",
                    "targets": [
                        {
                            "expr": "sum(genai_chatbot_chat_requests_total)",
                            "legendFormat": "Total Chat Requests"
                        }
                    ],
                    "fieldConfig": {
                        "defaults": {
                            "color": {
                                "mode": "palette-classic"
                            },
                            "custom": {
                                "displayMode": "gradient-gauge"
                            }
                        }
                    },
                    "gridPos": {
                        "h": 8,
                        "w": 6,
                        "x": 0,
                        "y": 0
                    }
                },
                {
                    "id": 2,
                    "title": "Chat Request Duration",
                    "type": "timeseries",
                    "targets": [
                        {
                            "expr": "rate(genai_chatbot_chat_request_duration_seconds_sum[5m])",
                            "legendFormat": "Duration"
                        }
                    ],
                    "fieldConfig": {
                        "defaults": {
                            "color": {
                                "mode": "palette-classic"
                            }
                        }
                    },
                    "gridPos": {
                        "h": 8,
                        "w": 12,
                        "x": 6,
                        "y": 0
                    }
                },
                {
                    "id": 3,
                    "title": "Tokens Used by Model",
                    "type": "timeseries",
                    "targets": [
                        {
                            "expr": "sum(rate(genai_chatbot_tokens_used_total[5m])) by (model)",
                            "legendFormat": "{{model}}"
                        }
                    ],
                    "fieldConfig": {
                        "defaults": {
                            "color": {
                                "mode": "palette-classic"
                            }
                        }
                    },
                    "gridPos": {
                        "h": 8,
                        "w": 12,
                        "x": 0,
                        "y": 8
                    }
                },
                {
                    "id": 4,
                    "title": "Cost by Model",
                    "type": "timeseries",
                    "targets": [
                        {
                            "expr": "sum(rate(genai_chatbot_cost_total[5m])) by (model)",
                            "legendFormat": "{{model}}"
                        }
                    ],
                    "fieldConfig": {
                        "defaults": {
                            "color": {
                                "mode": "palette-classic"
                            },
                            "unit": "currencyUSD"
                        }
                    },
                    "gridPos": {
                        "h": 8,
                        "w": 12,
                        "x": 12,
                        "y": 8
                    }
                },
                {
                    "id": 5,
                    "title": "Intent Classifications",
                    "type": "piechart",
                    "targets": [
                        {
                            "expr": "sum(genai_chatbot_intent_classifications_total) by (intent)",
                            "legendFormat": "{{intent}}"
                        }
                    ],
                    "fieldConfig": {
                        "defaults": {
                            "color": {
                                "mode": "palette-classic"
                            }
                        }
                    },
                    "gridPos": {
                        "h": 8,
                        "w": 8,
                        "x": 0,
                        "y": 16
                    }
                },
                {
                    "id": 6,
                    "title": "Knowledge Base Documents",
                    "type": "stat",
                    "targets": [
                        {
                            "expr": "genai_chatbot_knowledge_base_documents",
                            "legendFormat": "Documents in KB"
                        }
                    ],
                    "fieldConfig": {
                        "defaults": {
                            "color": {
                                "mode": "palette-classic"
                            },
                            "custom": {
                                "displayMode": "gradient-gauge"
                            }
                        }
                    },
                    "gridPos": {
                        "h": 8,
                        "w": 8,
                        "x": 8,
                        "y": 16
                    }
                },
                {
                    "id": 7,
                    "title": "HTTP Request Rate",
                    "type": "timeseries",
                    "targets": [
                        {
                            "expr": "sum(rate(http_requests_total[5m])) by (handler)",
                            "legendFormat": "{{handler}}"
                        }
                    ],
                    "fieldConfig": {
                        "defaults": {
                            "color": {
                                "mode": "palette-classic"
                            }
                        }
                    },
                    "gridPos": {
                        "h": 8,
                        "w": 12,
                        "x": 0,
                        "y": 24
                    }
                }
            ],
            "time": {
                "from": "now-1h",
                "to": "now"
            },
            "refresh": "10s"
        }
    }
    
    try:
        # Test connection to Grafana
        response = requests.get(f"{GRAFANA_URL}/api/health", auth=(USERNAME, PASSWORD))
        if response.status_code == 200:
            print("✅ Connected to Grafana successfully!")
        else:
            print(f"❌ Failed to connect to Grafana: {response.status_code}")
            return
        
        # Import dashboard
        import_url = f"{GRAFANA_URL}/api/dashboards/db"
        headers = {"Content-Type": "application/json"}
        
        response = requests.post(
            import_url,
            json=dashboard_json,
            auth=(USERNAME, PASSWORD),
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Dashboard imported successfully!")
            print(f"Dashboard ID: {result.get('id')}")
            print(f"Dashboard URL: {GRAFANA_URL}{result.get('url')}")
        else:
            print(f"❌ Failed to import dashboard: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to Grafana.")
        print("Make sure Grafana is running and port-forward is active:")
        print("kubectl port-forward svc/grafana-service 3000:3000 -n genai-chatbot")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Importing GenAI Chatbot Dashboard to Grafana...")
    import_dashboard() 