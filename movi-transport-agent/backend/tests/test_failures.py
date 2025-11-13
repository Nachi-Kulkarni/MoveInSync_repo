"""
Test Only Failed Tests

This script runs only the tests that were failing in the previous run.
"""

import asyncio
import httpx
import json
import time
from datetime import datetime
from typing import Dict, Any, List

# Configuration
BASE_URL = "http://localhost:8000"
AGENT_ENDPOINT = f"{BASE_URL}/api/v1/agent/message"

# Previously failed tests
FAILED_TESTS = [
    {
        "id": 5,
        "category": "READ - Static",
        "query": "List all stops for 'Path-2'",
        "expected_tool": "list_stops_for_path",
        "expected_success": True,
        "description": "Get ordered stops for a path"
    },
    {
        "id": 6,
        "category": "READ - Static",
        "query": "What stops are in Path-1?",
        "expected_tool": "list_stops_for_path",
        "expected_success": True,
        "description": "Alternative phrasing for path stops"
    },
    {
        "id": 7,
        "category": "READ - Static",
        "query": "Show me all routes that use 'Path-1'",
        "expected_tool": "list_routes_by_path",
        "expected_success": True,
        "description": "List routes using a specific path"
    },
    {
        "id": 8,
        "category": "READ - Static",
        "query": "Which routes go through Path-2?",
        "expected_tool": "list_routes_by_path",
        "expected_success": True,
        "description": "Alternative phrasing for routes by path"
    }
]

class TestLogger:
    def __init__(self):
        self.results: List[Dict[str, Any]] = []
        self.start_time = time.time()

    def log_test(self, test_case: Dict, response: Dict, duration: float, success: bool, notes: str = ""):
        result = {
            "test_id": test_case["id"],
            "category": test_case["category"],
            "query": test_case["query"],
            "expected_tool": test_case["expected_tool"],
            "actual_tool": response.get("tool_name"),
            "expected_success": test_case["expected_success"],
            "actual_success": success,
            "requires_confirmation": test_case.get("requires_confirmation", False),
            "got_confirmation": response.get("requires_confirmation", False),
            "response_type": response.get("response_type"),
            "duration_ms": round(duration * 1000, 2),
            "error": response.get("error"),
            "test_passed": success == test_case["expected_success"],
            "notes": notes,
            "timestamp": datetime.now().isoformat()
        }
        self.results.append(result)

    def print_summary(self):
        total_time = time.time() - self.start_time
        total = len(self.results)
        passed = sum(1 for r in self.results if r["test_passed"])
        failed = total - passed

        print("\n" + "="*80)
        print("FAILED TESTS RE-RUN RESULTS")
        print("="*80)
        print(f"\n📊 Results:")
        print(f"   Total Tests: {total}")
        print(f"   ✅ Passed: {passed} ({passed/total*100:.1f}%)")
        print(f"   ❌ Failed: {failed} ({failed/total*100:.1f}%)")
        print(f"   ⏱️  Total Time: {total_time:.2f}s")

        print(f"\n📋 Test Results:")
        print("-"*80)

        for r in self.results:
            status = "✅ PASS" if r["test_passed"] else "❌ FAIL"
            print(f"\n{status} | Test #{r['test_id']} - {r['category']}")
            print(f"   Query: \"{r['query']}\"")
            print(f"   Tool: {r['expected_tool']} → {r['actual_tool']}")
            print(f"   Success: {r['expected_success']} → {r['actual_success']}")
            print(f"   Duration: {r['duration_ms']}ms")
            if r["error"]:
                print(f"   Error: {r['error']}")
            if r["notes"]:
                print(f"   Notes: {r['notes']}")

        # Save to JSON
        output_file = "test_failures_results.json"
        with open(output_file, "w") as f:
            json.dump({
                "summary": {
                    "total": total,
                    "passed": passed,
                    "failed": failed,
                    "pass_rate": f"{passed/total*100:.1f}%",
                    "total_time": f"{total_time:.2f}s"
                },
                "results": self.results
            }, f, indent=2)

        print(f"\n💾 Results saved to: {output_file}")
        print("="*80 + "\n")

async def test_agent_query(query: str, session_id: str) -> Dict[str, Any]:
    async with httpx.AsyncClient(timeout=90.0) as client:
        response = await client.post(
            AGENT_ENDPOINT,
            json={
                "user_input": query,
                "session_id": session_id,
                "context": {"page": "busDashboard"}
            }
        )
        return response.json()

async def run_failed_tests():
    print("\n" + "="*80)
    print("RUNNING ONLY FAILED TESTS")
    print("="*80)
    print(f"\n🚀 Testing {len(FAILED_TESTS)} previously failed tests...\n")

    logger = TestLogger()

    for i, test_case in enumerate(FAILED_TESTS, 1):
        print(f"[{i}/{len(FAILED_TESTS)}] Testing: {test_case['query']}")

        session_id = f"test-failed-{test_case['id']}-{int(time.time())}"

        try:
            start = time.time()
            response = await test_agent_query(test_case["query"], session_id)
            duration = time.time() - start

            success = response.get("execution_success", False)
            notes = ""

            logger.log_test(test_case, response, duration, success, notes)

        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}" if str(e) else type(e).__name__
            logger.log_test(test_case, {"error": error_msg}, 0, False, f"Exception: {error_msg}")
            print(f"   ❌ Error: {error_msg}")

        await asyncio.sleep(0.5)

    logger.print_summary()

if __name__ == "__main__":
    print("\n" + "="*80)
    print("FAILED TESTS ONLY")
    print("="*80)

    asyncio.run(run_failed_tests())