#!/usr/bin/env python3
"""
Test script to verify Prometheus metrics are working
"""
from prometheus_client import generate_latest, REGISTRY
from app.utils.metrics import CHAT_REQUESTS_TOTAL, record_chat_metrics

def test_metrics():
    print("Testing Prometheus metrics...")
    
    # Test recording metrics
    print("Recording test metrics...")
    record_chat_metrics(
        user_id="test_user",
        intent="test",
        response_type="test",
        duration=1.0,
        tokens=100,
        cost=0.01,
        model="gpt-4"
    )
    
    # Generate metrics output
    print("Generating metrics output...")
    metrics_output = generate_latest().decode('utf-8')
    
    # Check for our custom metrics
    if 'genai_chatbot_chat_requests_total' in metrics_output:
        print("✅ Custom metrics found!")
        print("Metrics output:")
        print(metrics_output)
    else:
        print("❌ Custom metrics not found!")
        print("Available metrics:")
        for metric in REGISTRY.collect():
            print(f"  - {metric.name}")

if __name__ == "__main__":
    test_metrics() 