#!/usr/bin/env python3
"""
Simple End-to-End Test - Quick health check with basic functionality
Usage: python 1-simple-test.py
"""

import requests
import json
import time
import sys
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"
DELAY_BETWEEN_TESTS = 1

class SimpleTestRunner:
    def __init__(self):
        self.test_results = []
        self.passed = 0
        self.failed = 0

    def print_header(self):
        print("🚀 SIMPLE END-TO-END TEST")
        print("=" * 40)
        print(f"Base URL: {BASE_URL}")
        print()

    def test_endpoint(self, name: str, test_function):
        print(f"🧪 Testing {name}...", end=" ")
        try:
            result = test_function()
            if result:
                print("✅ PASS")
                self.passed += 1
                self.test_results.append(f"{name}: PASS")
            else:
                print("❌ FAIL")
                self.failed += 1
                self.test_results.append(f"{name}: FAIL")
        except Exception as e:
            print(f"❌ FAIL - {str(e)}")
            self.failed += 1
            self.test_results.append(f"{name}: FAIL - {str(e)}")
        
        time.sleep(DELAY_BETWEEN_TESTS)

    def test_health_check(self) -> bool:
        """Test health endpoint"""
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        data = response.json()
        return data.get("status") == "healthy"

    def test_direct_chat(self) -> bool:
        """Test direct chat functionality"""
        payload = {
            "message": "Hello, this is a simple test",
            "user_id": "simple_test_user",
            "use_rag": False
        }
        response = requests.post(
            f"{BASE_URL}/chat",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        data = response.json()
        return data.get("response_type") == "chat" and data.get("response")

    def test_rag_chat(self) -> bool:
        """Test RAG chat functionality"""
        payload = {
            "message": "What are proteins made of?",
            "user_id": "simple_rag_user",
            "use_rag": True
        }
        response = requests.post(
            f"{BASE_URL}/chat",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        data = response.json()
        return data.get("response_type") == "rag" and data.get("response")

    def test_knowledge_base_stats(self) -> bool:
        """Test knowledge base stats endpoint"""
        response = requests.get(f"{BASE_URL}/knowledge-base/stats", timeout=10)
        data = response.json()
        return data.get("total_documents", -1) >= 0

    def test_metrics_endpoint(self) -> bool:
        """Test metrics endpoint"""
        response = requests.get(f"{BASE_URL}/metrics", timeout=10)
        content = response.text
        return "genai_chatbot_" in content

    def print_results(self):
        print()
        print("📊 SIMPLE TEST RESULTS")
        print("=" * 25)
        print(f"Total Tests: {self.passed + self.failed}")
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")

        success_rate = (self.passed / (self.passed + self.failed) * 100) if (self.passed + self.failed) > 0 else 0

        if success_rate >= 80:
            print(f"🎉 Success Rate: {success_rate:.1f}% - PASSED!")
            print("✅ System is healthy and ready for use.")
        else:
            print(f"⚠️ Success Rate: {success_rate:.1f}% - FAILED!")
            print("❌ System needs attention.")

        print()
        print("💡 Next steps:")
        print("   - Run: python 2-comprehensive-test.py for full testing")
        print("   - Run: python 3-stress-test.py for load testing")

    def run_all_tests(self):
        self.print_header()
        
        # Run all tests
        self.test_endpoint("Health Check", self.test_health_check)
        self.test_endpoint("Direct Chat", self.test_direct_chat)
        self.test_endpoint("RAG Chat", self.test_rag_chat)
        self.test_endpoint("Knowledge Base Stats", self.test_knowledge_base_stats)
        self.test_endpoint("Metrics Endpoint", self.test_metrics_endpoint)
        
        self.print_results()
        
        # Exit with appropriate code
        sys.exit(0 if self.failed == 0 else 1)

if __name__ == "__main__":
    runner = SimpleTestRunner()
    runner.run_all_tests()
