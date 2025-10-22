#!/usr/bin/env python3
"""
Comprehensive Functional Test - Complete end-to-end testing with all scenarios
Usage: python 2-comprehensive-test.py [--verbose] [--delay SECONDS]
"""

import requests
import json
import time
import sys
import argparse
from datetime import datetime
from typing import Dict, Any, List

class ComprehensiveTestRunner:
    def __init__(self, base_url: str = "http://localhost:8000", delay: int = 2, verbose: bool = False):
        self.base_url = base_url
        self.delay = delay
        self.verbose = verbose
        self.results = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "details": []
        }

    def print_header(self):
        print("🔬 COMPREHENSIVE FUNCTIONAL TEST")
        print("=" * 50)
        print(f"Base URL: {self.base_url}")
        print(f"Delay: {self.delay} seconds")
        print(f"Verbose: {self.verbose}")
        print()

    def log_result(self, test_name: str, passed: bool, details: str = "", response: Any = None):
        self.results["total"] += 1
        if passed:
            self.results["passed"] += 1
            print(f"✅ PASS: {test_name}")
            if self.verbose and details:
                print(f"   Details: {details}")
        else:
            self.results["failed"] += 1
            print(f"❌ FAIL: {test_name}")
            if details:
                print(f"   Error: {details}")

        self.results["details"].append({
            "test": test_name,
            "passed": passed,
            "details": details,
            "response": str(response) if response else None,
            "timestamp": datetime.now().isoformat()
        })

    def test_with_error_handling(self, test_name: str, test_function):
        print(f"🧪 {test_name}...")
        try:
            test_function()
        except Exception as e:
            self.log_result(test_name, False, str(e))
        time.sleep(self.delay)

    def run_health_tests(self):
        print("🏥 HEALTH & CONNECTIVITY TESTS")
        print("-" * 35)

        def test_health_endpoint():
            response = requests.get(f"{self.base_url}/health", timeout=10)
            data = response.json()
            passed = data.get("status") == "healthy"
            self.log_result("Health Endpoint", passed, f"Status: {data.get('status')}", data)

        def test_metrics_endpoint():
            response = requests.get(f"{self.base_url}/metrics", timeout=10)
            content = response.text
            custom_metrics = content.count("genai_chatbot_")
            passed = custom_metrics > 0
            self.log_result("Metrics Endpoint", passed, f"Found {custom_metrics} custom metrics")

        self.test_with_error_handling("Health Endpoint", test_health_endpoint)
        self.test_with_error_handling("Metrics Endpoint", test_metrics_endpoint)

    def run_chat_tests(self):
        print()
        print("💬 CHAT FUNCTIONALITY TESTS")
        print("-" * 30)

        # Direct Chat Tests
        direct_tests = [
            {"message": "Hello, how are you?", "intent": "general", "user_id": "test_direct_1"},
            {"message": "Can you help me with something?", "intent": "help", "user_id": "test_direct_2"},
            {"message": "What is machine learning?", "intent": "technical", "user_id": "test_direct_3"}
        ]

        for test in direct_tests:
            def test_direct_chat():
                payload = {
                    "message": test["message"],
                    "user_id": test["user_id"],
                    "use_rag": False
                }
                response = requests.post(
                    f"{self.base_url}/chat",
                    json=payload,
                    timeout=30
                )
                data = response.json()
                passed = (data.get("response_type") == "chat" and 
                         data.get("response") and 
                         data.get("sources_used") == 0)
                details = f"Type: {data.get('response_type')}, Sources: {data.get('sources_used')}"
                self.log_result(f"Direct Chat - {test['intent']}", passed, details, data)

            self.test_with_error_handling(f"Direct Chat - {test['intent']}", test_direct_chat)

        # RAG Chat Tests
        rag_tests = [
            {"message": "What are amino acids?", "intent": "knowledge", "user_id": "test_rag_1"},
            {"message": "Tell me about protein structure", "intent": "knowledge", "user_id": "test_rag_2"},
            {"message": "How do proteins fold?", "intent": "technical", "user_id": "test_rag_3"}
        ]

        for test in rag_tests:
            def test_rag_chat():
                payload = {
                    "message": test["message"],
                    "user_id": test["user_id"],
                    "use_rag": True
                }
                response = requests.post(
                    f"{self.base_url}/chat",
                    json=payload,
                    timeout=30
                )
                data = response.json()
                passed = data.get("response_type") == "rag" and data.get("response")
                details = f"Type: {data.get('response_type')}, Sources: {data.get('sources_used')}"
                self.log_result(f"RAG Chat - {test['intent']}", passed, details, data)

            self.test_with_error_handling(f"RAG Chat - {test['intent']}", test_rag_chat)

    def run_knowledge_base_tests(self):
        print()
        print("📚 KNOWLEDGE BASE TESTS")
        print("-" * 25)

        def test_kb_stats():
            response = requests.get(f"{self.base_url}/knowledge-base/stats", timeout=10)
            data = response.json()
            passed = data.get("total_documents", -1) >= 0
            details = f"Documents: {data.get('total_documents')}, Chunks: {data.get('total_chunks')}"
            self.log_result("Knowledge Base Stats", passed, details, data)

        def test_kb_initialization():
            response = requests.post(f"{self.base_url}/knowledge-base/initialize", timeout=30)
            data = response.json()
            passed = data.get("success") == True
            details = f"Success: {data.get('success')}, Message: {data.get('message')}"
            self.log_result("Knowledge Base Initialization", passed, details, data)

        self.test_with_error_handling("Knowledge Base Stats", test_kb_stats)
        self.test_with_error_handling("Knowledge Base Initialization", test_kb_initialization)

    def run_error_handling_tests(self):
        print()
        print("⚠️ ERROR HANDLING TESTS")
        print("-" * 24)

        def test_invalid_json():
            try:
                response = requests.post(
                    f"{self.base_url}/chat",
                    data="invalid json",
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                self.log_result("Invalid JSON Handling", False, "Should have failed but didn't")
            except requests.exceptions.RequestException as e:
                passed = "400" in str(e) or "Bad Request" in str(e)
                self.log_result("Invalid JSON Handling", passed, "Correctly rejected invalid JSON")

        def test_missing_fields():
            try:
                payload = {"message": "test"}  # Missing user_id and use_rag
                response = requests.post(
                    f"{self.base_url}/chat",
                    json=payload,
                    timeout=10
                )
                if response.status_code in [400, 422]:
                    self.log_result("Missing Required Fields", True, "Correctly rejected missing fields")
                else:
                    self.log_result("Missing Required Fields", False, "Should have failed but didn't")
            except requests.exceptions.RequestException:
                self.log_result("Missing Required Fields", True, "Correctly rejected missing fields")

        def test_nonexistent_endpoint():
            try:
                response = requests.get(f"{self.base_url}/nonexistent", timeout=10)
                passed = response.status_code == 404
                self.log_result("Non-existent Endpoint", passed, f"Status: {response.status_code}")
            except requests.exceptions.RequestException as e:
                passed = "404" in str(e)
                self.log_result("Non-existent Endpoint", passed, "Correctly returned 404")

        self.test_with_error_handling("Invalid JSON Handling", test_invalid_json)
        self.test_with_error_handling("Missing Required Fields", test_missing_fields)
        self.test_with_error_handling("Non-existent Endpoint", test_nonexistent_endpoint)

    def run_memory_tests(self):
        print()
        print("🧠 CONVERSATION MEMORY TESTS")
        print("-" * 30)

        def test_conversation_memory():
            user_id = "memory_test_user"
            
            # First message
            payload1 = {"message": "My name is Alice", "user_id": user_id, "use_rag": False}
            response1 = requests.post(f"{self.base_url}/chat", json=payload1, timeout=30)
            data1 = response1.json()
            
            time.sleep(1)
            
            # Second message referring to first
            payload2 = {"message": "What is my name?", "user_id": user_id, "use_rag": False}
            response2 = requests.post(f"{self.base_url}/chat", json=payload2, timeout=30)
            data2 = response2.json()
            
            passed = (data1.get("response") and data2.get("response") and 
                     "alice" in data2.get("response", "").lower())
            details = f"Memory working: {'alice' in data2.get('response', '').lower()}"
            self.log_result("Conversation Memory - Multiple Turns", passed, details)

        self.test_with_error_handling("Conversation Memory - Multiple Turns", test_conversation_memory)

    def run_performance_tests(self):
        print()
        print("⚡ PERFORMANCE TESTS")
        print("-" * 20)

        def test_response_time():
            start_time = time.time()
            payload = {"message": "Quick response test", "user_id": "perf_test", "use_rag": False}
            response = requests.post(f"{self.base_url}/chat", json=payload, timeout=30)
            end_time = time.time()
            
            response_time_ms = (end_time - start_time) * 1000
            data = response.json()
            passed = response_time_ms < 10000 and data.get("response")  # Less than 10 seconds
            details = f"Response time: {response_time_ms:.0f}ms"
            self.log_result("Response Time Test", passed, details)

        self.test_with_error_handling("Response Time Test", test_response_time)

    def print_final_results(self):
        print()
        print("📊 COMPREHENSIVE TEST RESULTS")
        print("=" * 35)
        print(f"Total Tests: {self.results['total']}")
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")

        success_rate = (self.results['passed'] / self.results['total'] * 100) if self.results['total'] > 0 else 0

        if success_rate >= 85:
            print(f"🎉 Success Rate: {success_rate:.1f}% - COMPREHENSIVE TEST PASSED!")
            print("   System is fully functional and ready for production.")
        elif success_rate >= 70:
            print(f"⚠️ Success Rate: {success_rate:.1f}% - PARTIAL SUCCESS")
            print("   Some issues found that need attention.")
        else:
            print(f"❌ Success Rate: {success_rate:.1f}% - COMPREHENSIVE TEST FAILED!")
            print("   Critical issues found. System needs attention.")

        # Save detailed results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"comprehensive_test_results_{timestamp}.json"
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print()
        print(f"📄 Detailed results saved to: {results_file}")
        print()
        print("💡 Next steps:")
        print("   - Run: python 3-stress-test.py for load testing")
        print(f"   - Check metrics at {self.base_url}/metrics")

    def run_all_tests(self):
        self.print_header()
        
        self.run_health_tests()
        self.run_chat_tests()
        self.run_knowledge_base_tests()
        self.run_error_handling_tests()
        self.run_memory_tests()
        self.run_performance_tests()
        
        self.print_final_results()
        
        # Exit with appropriate code
        success_rate = (self.results['passed'] / self.results['total'] * 100) if self.results['total'] > 0 else 0
        sys.exit(0 if success_rate >= 70 else 1)

def main():
    parser = argparse.ArgumentParser(description="Comprehensive GenAI Chatbot Test Suite")
    parser.add_argument("--base-url", default="http://localhost:8000", help="Base URL for the API")
    parser.add_argument("--delay", type=int, default=2, help="Delay between tests in seconds")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    
    args = parser.parse_args()
    
    runner = ComprehensiveTestRunner(
        base_url=args.base_url,
        delay=args.delay,
        verbose=args.verbose
    )
    runner.run_all_tests()

if __name__ == "__main__":
    main()
