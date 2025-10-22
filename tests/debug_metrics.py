#!/usr/bin/env python3
"""
Debug script to test metrics registration
"""
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from prometheus_client import REGISTRY, generate_latest
    print("✅ prometheus_client imported successfully")
    
    # Import our metrics
    from app.utils.metrics import CHAT_REQUESTS_TOTAL
    print("✅ Custom metrics imported successfully")
    
    # Check if metric is registered
    metrics = list(REGISTRY.collect())
    custom_metrics = [m for m in metrics if 'genai_chatbot' in m.name]
    
    if custom_metrics:
        print("✅ Custom metrics found in registry:")
        for metric in custom_metrics:
            print(f"  - {metric.name}")
    else:
        print("❌ No custom metrics found in registry")
        print("Available metrics:")
        for metric in metrics:
            print(f"  - {metric.name}")
    
    # Test recording a metric
    print("\nTesting metric recording...")
    CHAT_REQUESTS_TOTAL.labels(user_id="test", intent="test", response_type="test").inc()
    
    # Check again
    metrics_after = list(REGISTRY.collect())
    custom_metrics_after = [m for m in metrics_after if 'genai_chatbot' in m.name]
    
    if custom_metrics_after:
        print("✅ Custom metrics still found after recording")
        metrics_output = generate_latest().decode('utf-8')
        if 'genai_chatbot_chat_requests_total' in metrics_output:
            print("✅ Custom metrics appear in output!")
        else:
            print("❌ Custom metrics not in output")
    else:
        print("❌ Custom metrics disappeared after recording")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc() 