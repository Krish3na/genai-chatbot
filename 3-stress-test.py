#!/usr/bin/env python3
"""
Stress Test - Load testing with 20+ requests, concurrent testing, and edge cases
Usage: python 3-stress-test.py [--requests 25] [--concurrent 5] [--verbose]
"""

import requests
import json
import time
import sys
import argparse
import threading
import statistics
from datetime import datetime
from typing import Dict, Any, List
from concurrent.futures import ThreadPoolExecutor, as_completed

class StressTestRunner:
    def __init__(self, base_url: str = "http://localhost:8080", 
                 total_requests: int = 25, concurrent_users: int = 5, verbose: bool = False):
        self.base_url = base_url
        self.total_requests = total_requests
        self.concurrent_users = concurrent_users
        self.verbose = verbose
        
        self.results = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "response_times": [],
            "errors": [],
            "start_time": None,
            "end_time": None
        }
        
        self.lock = threading.Lock()

    def print_header(self):
        print("🚀 STRESS TEST & LOAD TESTING")
        print("=" * 50)
        print(f"Base URL: {self.base_url}")
        print(f"Total Requests: {self.total_requests}")
        print(f"Concurrent Users: {self.concurrent_users}")
        print(f"Verbose: {self.verbose}")
        print()

    def send_chat_request(self, user_id: str, message: str, use_rag: bool = False, request_id: str = ""):
        """Send a single chat request and record results"""
        try:
            start_time = time.time()
            
            payload = {
                "message": message,
                "user_id": user_id,
                "use_rag": use_rag
            }
            
            response = requests.post(
                f"{self.base_url}/chat",
                json=payload,
                timeout=30
            )
            
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds
            
            data = response.json()
            
            with self.lock:
                self.results["total_requests"] += 1
                self.results["successful_requests"] += 1
                self.results["response_times"].append(response_time)
            
            if self.verbose:
                print(f"✅ Request {request_id} completed in {response_time:.0f}ms")
            
            return {
                "success": True,
                "response_time": response_time,
                "response": data,
                "error": None
            }
            
        except Exception as e:
            with self.lock:
                self.results["total_requests"] += 1
                self.results["failed_requests"] += 1
                self.results["errors"].append(str(e))
            
            if self.verbose:
                print(f"❌ Request {request_id} failed: {str(e)}")
            
            return {
                "success": False,
                "response_time": 0,
                "response": None,
                "error": str(e)
            }

    def run_preflight_checks(self):
        """Run pre-flight checks before starting stress test"""
        print("🔍 PRE-FLIGHT CHECKS")
        print("-" * 20)
        
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            data = response.json()
            if data.get("status") == "healthy":
                print("✅ Service is healthy and ready for stress testing")
                return True
            else:
                print(f"⚠️ Service health check returned: {data.get('status')}")
                return False
        except Exception as e:
            print(f"❌ Pre-flight check failed: {str(e)}")
            print("   Cannot proceed with stress testing.")
            return False

    def run_load_test(self):
        """Run the main load test with concurrent requests"""
        print()
        print("⚡ LOAD TEST SCENARIOS")
        print("-" * 22)
        
        # Define test scenarios with different weights
        scenarios = [
            {"type": "Direct", "message": "Hello, this is load test message", "use_rag": False, "weight": 40},
            {"type": "RAG", "message": "What are amino acids and their properties?", "use_rag": True, "weight": 30},
            {"type": "Help", "message": "Can you help me understand proteins?", "use_rag": False, "weight": 15},
            {"type": "Technical", "message": "Explain protein folding mechanisms", "use_rag": True, "weight": 15}
        ]
        
        print("🔄 Starting concurrent batch testing...")
        
        self.results["start_time"] = datetime.now()
        
        # Create requests list
        requests_list = []
        for i in range(self.total_requests):
            # Select scenario based on weight (simplified)
            import random
            rand = random.randint(1, 100)
            if rand <= 40:
                scenario = scenarios[0]
            elif rand <= 70:
                scenario = scenarios[1]
            elif rand <= 85:
                scenario = scenarios[2]
            else:
                scenario = scenarios[3]
            
            user_id = f"stress_user_{i % self.concurrent_users}_{i}"
            request_id = f"req_{i+1}"
            
            requests_list.append({
                "user_id": user_id,
                "message": scenario["message"],
                "use_rag": scenario["use_rag"],
                "request_id": request_id,
                "scenario_type": scenario["type"]
            })
        
        # Execute requests concurrently
        with ThreadPoolExecutor(max_workers=self.concurrent_users) as executor:
            future_to_request = {
                executor.submit(
                    self.send_chat_request,
                    req["user_id"],
                    req["message"],
                    req["use_rag"],
                    req["request_id"]
                ): req for req in requests_list
            }
            
            completed = 0
            for future in as_completed(future_to_request):
                completed += 1
                if not self.verbose and completed % 5 == 0:
                    print(f"📊 Completed {completed}/{self.total_requests} requests...")
        
        self.results["end_time"] = datetime.now()
        print(f"✅ All {self.total_requests} requests completed!")

    def run_edge_case_tests(self):
        """Test edge cases and error scenarios"""
        print()
        print("🎯 EDGE CASE TESTING")
        print("-" * 21)
        
        # Very long message test
        print("🧪 Testing very long message...")
        long_message = "This is a very long message. " * 200
        long_result = self.send_chat_request("edge_case_long", long_message, request_id="long_msg")
        
        # Empty message test
        print("🧪 Testing empty message handling...")
        try:
            payload = {"message": "", "user_id": "edge_case_empty", "use_rag": False}
            response = requests.post(f"{self.base_url}/chat", json=payload, timeout=10)
            if response.status_code == 200:
                print("⚠️ Empty message was accepted (might be expected behavior)")
            else:
                print("✅ Empty message correctly rejected")
        except Exception:
            print("✅ Empty message correctly rejected")
        
        # Special characters test
        print("🧪 Testing special characters...")
        special_message = "Test with emojis 🚀🔬 and special chars: @#$%^&*()[]{}|;':,.<>?/~`"
        special_result = self.send_chat_request("edge_case_special", special_message, request_id="special_chars")

    def analyze_results(self):
        """Analyze and display test results"""
        print()
        print("📊 STRESS TEST RESULTS & ANALYSIS")
        print("=" * 45)
        
        duration = (self.results["end_time"] - self.results["start_time"]).total_seconds()
        requests_per_second = self.results["total_requests"] / duration if duration > 0 else 0
        
        print(f"⏱️ Test Duration: {duration:.2f} seconds")
        print(f"📈 Total Requests: {self.results['total_requests']}")
        print(f"✅ Successful: {self.results['successful_requests']}")
        print(f"❌ Failed: {self.results['failed_requests']}")
        print(f"🚀 Requests/Second: {requests_per_second:.2f}")
        
        if self.results["response_times"]:
            avg_response_time = statistics.mean(self.results["response_times"])
            min_response_time = min(self.results["response_times"])
            max_response_time = max(self.results["response_times"])
            
            # Calculate 95th percentile
            sorted_times = sorted(self.results["response_times"])
            p95_index = int(len(sorted_times) * 0.95)
            p95_response_time = sorted_times[p95_index] if p95_index < len(sorted_times) else max_response_time
            
            print()
            print("⚡ RESPONSE TIME ANALYSIS:")
            print(f"   Average: {avg_response_time:.2f}ms")
            print(f"   Minimum: {min_response_time:.2f}ms")
            print(f"   Maximum: {max_response_time:.2f}ms")
            print(f"   95th Percentile: {p95_response_time:.2f}ms")
        
        success_rate = (self.results["successful_requests"] / self.results["total_requests"] * 100) if self.results["total_requests"] > 0 else 0
        
        print()
        print(f"🎯 SUCCESS RATE: {success_rate:.1f}%")
        
        # Performance assessment
        if success_rate >= 95 and avg_response_time < 5000:
            print()
            print("🏆 EXCELLENT PERFORMANCE!")
            print("   System handles load very well.")
        elif success_rate >= 85 and avg_response_time < 10000:
            print()
            print("✅ GOOD PERFORMANCE")
            print("   System performs adequately under load.")
        else:
            print()
            print("⚠️ PERFORMANCE ISSUES DETECTED")
            print("   System may need optimization.")
        
        # Error analysis
        if self.results["errors"]:
            print()
            print("🔍 ERROR ANALYSIS:")
            from collections import Counter
            error_counts = Counter(self.results["errors"])
            for error, count in error_counts.most_common(5):
                print(f"   {count}x: {error}")
        
        # Save detailed results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"stress_test_results_{timestamp}.json"
        
        # Prepare results for JSON serialization
        json_results = {
            **self.results,
            "start_time": self.results["start_time"].isoformat() if self.results["start_time"] else None,
            "end_time": self.results["end_time"].isoformat() if self.results["end_time"] else None,
            "duration_seconds": duration,
            "requests_per_second": requests_per_second,
            "success_rate": success_rate
        }
        
        if self.results["response_times"]:
            json_results.update({
                "avg_response_time": avg_response_time,
                "min_response_time": min_response_time,
                "max_response_time": max_response_time,
                "p95_response_time": p95_response_time
            })
        
        with open(results_file, 'w') as f:
            json.dump(json_results, f, indent=2)
        
        print()
        print(f"📄 Detailed results saved to: {results_file}")
        
        print()
        print("💡 Recommendations:")
        if success_rate < 95:
            print("   • Investigate failed requests and error patterns")
        if avg_response_time > 3000:
            print("   • Consider response time optimization")
        if requests_per_second < 5:
            print("   • System may need performance tuning for higher throughput")
        print(f"   • Monitor metrics at {self.base_url}/metrics")
        print("   • Check system resources (CPU, memory, network)")
        
        return success_rate

    def run_all_tests(self):
        """Run all stress tests"""
        self.print_header()
        
        # Pre-flight checks
        if not self.run_preflight_checks():
            sys.exit(1)
        
        # Main load test
        self.run_load_test()
        
        # Edge case tests
        self.run_edge_case_tests()
        
        # Analyze results
        success_rate = self.analyze_results()
        
        # Exit with appropriate code
        sys.exit(0 if success_rate >= 85 else 1)

def main():
    parser = argparse.ArgumentParser(description="Stress Test for GenAI Chatbot")
    parser.add_argument("--base-url", default="http://localhost:8080", help="Base URL for the API")
    parser.add_argument("--requests", type=int, default=25, help="Total number of requests to send")
    parser.add_argument("--concurrent", type=int, default=5, help="Number of concurrent users")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    
    args = parser.parse_args()
    
    runner = StressTestRunner(
        base_url=args.base_url,
        total_requests=args.requests,
        concurrent_users=args.concurrent,
        verbose=args.verbose
    )
    runner.run_all_tests()

if __name__ == "__main__":
    main()
