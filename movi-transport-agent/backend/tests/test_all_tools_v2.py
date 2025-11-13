"""
Comprehensive Tool Testing Suite v2 - With Database Cleanup

Tests all 9 tool functions with 20 different queries covering:
- Read operations (static and dynamic)
- Create operations (static and dynamic)
- Delete operations (high-risk with consequences)
- Edge cases and error handling

IMPROVEMENTS in v2:
- Automatic database cleanup before tests
- Test data setup for reliable execution
- Optional cleanup after tests
- Better error reporting

Usage:
    python tests/test_all_tools_v2.py [--no-cleanup-after]
"""

import asyncio
import httpx
import json
import time
import sys
from datetime import datetime
from typing import Dict, Any, List
from test_cleanup import DatabaseCleanup


# Configuration
BASE_URL = "http://localhost:8000"
AGENT_ENDPOINT = f"{BASE_URL}/api/v1/agent/message"


# Test cases organized by tool category
TEST_CASES = [
    # ========== READ TOOLS (Dynamic Assets) ==========
    {
        "id": 1,
        "category": "READ - Dynamic",
        "tool": "get_unassigned_vehicles_count",
        "query": "How many unassigned vehicles are there?",
        "expected_tool": "get_unassigned_vehicles_count",
        "expected_success": True,
        "description": "List all vehicles without deployments"
    },
    {
        "id": 2,
        "category": "READ - Dynamic",
        "tool": "get_unassigned_vehicles_count",
        "query": "Show me available vehicles",
        "expected_tool": "get_unassigned_vehicles_count",
        "expected_success": True,
        "description": "Alternative phrasing for unassigned vehicles"
    },
    {
        "id": 3,
        "category": "READ - Dynamic",
        "tool": "get_trip_status",
        "query": "What's the status of the 'Bulk - 00:01' trip?",
        "expected_tool": "get_trip_status",
        "expected_success": True,
        "description": "Get trip details by name"
    },
    {
        "id": 4,
        "category": "READ - Dynamic",
        "tool": "get_trip_status",
        "query": "Show me details for trip 6",
        "expected_tool": "get_trip_status",
        "expected_success": True,
        "description": "Get trip details by ID"
    },

    # ========== READ TOOLS (Static Assets) ==========
    {
        "id": 5,
        "category": "READ - Static",
        "tool": "list_stops_for_path",
        "query": "List all stops for 'Path-2'",
        "expected_tool": "list_stops_for_path",
        "expected_success": True,
        "description": "Get ordered stops for a path"
    },
    {
        "id": 6,
        "category": "READ - Static",
        "tool": "list_stops_for_path",
        "query": "What stops are in Path-1?",
        "expected_tool": "list_stops_for_path",
        "expected_success": True,
        "description": "Alternative phrasing for path stops"
    },
    {
        "id": 7,
        "category": "READ - Static",
        "tool": "list_routes_by_path",
        "query": "Show me all routes that use 'Path-1'",
        "expected_tool": "list_routes_by_path",
        "expected_success": True,
        "description": "List routes using a specific path"
    },
    {
        "id": 8,
        "category": "READ - Static",
        "tool": "list_routes_by_path",
        "query": "Which routes go through Path-2?",
        "expected_tool": "list_routes_by_path",
        "expected_success": True,
        "description": "Alternative phrasing for routes by path"
    },

    # ========== CREATE TOOLS (Dynamic Assets) ==========
    {
        "id": 9,
        "category": "CREATE - Dynamic",
        "tool": "assign_vehicle_to_trip",
        "query": "Assign vehicle 'KA-01-AB-1234' to trip 1",
        "expected_tool": "assign_vehicle_to_trip",
        "expected_success": True,
        "description": "Assign vehicle by license plate and trip ID"
    },
    {
        "id": 10,
        "category": "CREATE - Dynamic",
        "tool": "assign_vehicle_to_trip",
        "query": "Put vehicle 'MH-12-GH-3456' on trip 2",
        "expected_tool": "assign_vehicle_to_trip",
        "expected_success": True,
        "description": "Assign vehicle to trip without existing vehicle (trip 2)"
    },

    # ========== CREATE TOOLS (Static Assets) ==========
    {
        "id": 11,
        "category": "CREATE - Static",
        "tool": "create_stop",
        "query": "Create a new stop called 'Odeon Circle' at coordinates 12.9716, 77.5946",
        "expected_tool": "create_stop",
        "expected_success": True,
        "description": "Create new geographic stop"
    },
    {
        "id": 12,
        "category": "CREATE - Static",
        "tool": "create_stop",
        "query": "Add a stop named 'MG Road Metro' at latitude 12.9758 and longitude 77.6065",
        "expected_tool": "create_stop",
        "expected_success": True,
        "description": "Alternative phrasing for stop creation"
    },
    {
        "id": 13,
        "category": "CREATE - Static",
        "tool": "create_path",
        "query": "Create a new path called 'Tech-Loop' using stops 1, 3, 5, 7",
        "expected_tool": "create_path",
        "expected_success": True,
        "description": "Create path with stop IDs"
    },
    {
        "id": 14,
        "category": "CREATE - Static",
        "tool": "create_path",
        "query": "Make a path named 'Metro-Route' with stops [2, 4, 6, 8]",
        "expected_tool": "create_path",
        "expected_success": True,
        "description": "Alternative phrasing for path creation"
    },
    {
        "id": 15,
        "category": "CREATE - Static",
        "tool": "create_route",
        "query": "Create a route for 'Path-1' at 08:30 LOGIN direction",
        "expected_tool": "create_route",
        "expected_success": True,
        "description": "Create morning LOGIN route"
    },
    {
        "id": 16,
        "category": "CREATE - Static",
        "tool": "create_route",
        "query": "Add a LOGOUT route on Path-2 at 18:45",
        "expected_tool": "create_route",
        "expected_success": True,
        "description": "Create evening LOGOUT route"
    },

    # ========== DELETE TOOLS (High-Risk with Consequences) ==========
    {
        "id": 17,
        "category": "DELETE - High Risk",
        "tool": "remove_vehicle_from_trip",
        "query": "Remove the vehicle from 'Hollilux - BTS - 17:00'",
        "expected_tool": "remove_vehicle_from_trip",
        "expected_success": True,  # Success = confirmation properly triggered
        "requires_confirmation": True,
        "description": "Remove vehicle from 50% booked trip (HIGH RISK) - Now has vehicle assigned"
    },
    {
        "id": 18,
        "category": "DELETE - High Risk",
        "tool": "remove_vehicle_from_trip",
        "query": "Unassign vehicle from trip 1",
        "expected_tool": "remove_vehicle_from_trip",
        "expected_success": True,  # Success = confirmation properly triggered
        "requires_confirmation": True,
        "description": "Remove vehicle from 25% booked trip (MEDIUM RISK)"
    },

    # ========== EDGE CASES & ERROR HANDLING ==========
    {
        "id": 19,
        "category": "EDGE CASE - Not Found",
        "tool": "get_trip_status",
        "query": "What's the status of trip 999?",
        "expected_tool": "get_trip_status",
        "expected_success": False,
        "description": "Query non-existent trip ID"
    },
    {
        "id": 20,
        "category": "EDGE CASE - Complex Query",
        "tool": "get_unassigned_vehicles_count",
        "query": "How many vehicles are available near Koramangala?",
        "expected_tool": "get_unassigned_vehicles_count",
        "expected_success": True,
        "description": "Complex query with location (should ignore location filter)"
    },
]


class TestLogger:
    """Logger for test results with detailed tracking."""

    def __init__(self):
        self.results: List[Dict[str, Any]] = []
        self.start_time = time.time()

    def log_test(self, test_case: Dict, response: Dict, duration: float, success: bool, notes: str = ""):
        """Log a single test result."""
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
        """Print detailed test summary."""
        total_time = time.time() - self.start_time

        print("\n" + "="*80)
        print("MOVI TRANSPORT AGENT - COMPREHENSIVE TOOL TEST RESULTS v2")
        print("="*80)

        # Overall stats
        total = len(self.results)
        passed = sum(1 for r in self.results if r["test_passed"])
        failed = total - passed

        print(f"\n📊 Overall Results:")
        print(f"   Total Tests: {total}")
        print(f"   ✅ Passed: {passed} ({passed/total*100:.1f}%)")
        print(f"   ❌ Failed: {failed} ({failed/total*100:.1f}%)")
        print(f"   ⏱️  Total Time: {total_time:.2f}s")
        print(f"   📈 Avg Time/Test: {total_time/total:.2f}s")

        # Category breakdown
        print(f"\n📂 Results by Category:")
        categories = {}
        for r in self.results:
            cat = r["category"]
            if cat not in categories:
                categories[cat] = {"total": 0, "passed": 0}
            categories[cat]["total"] += 1
            if r["test_passed"]:
                categories[cat]["passed"] += 1

        for cat, stats in sorted(categories.items()):
            pct = stats["passed"]/stats["total"]*100
            status = "✅" if pct == 100 else "⚠️" if pct >= 50 else "❌"
            print(f"   {status} {cat:30s} {stats['passed']}/{stats['total']} ({pct:.0f}%)")

        # Detailed results
        print(f"\n📋 Detailed Test Results:")
        print("-"*80)

        for r in self.results:
            status = "✅ PASS" if r["test_passed"] else "❌ FAIL"
            print(f"\n{status} | Test #{r['test_id']} - {r['category']}")
            print(f"   Query: \"{r['query']}\"")
            print(f"   Tool: {r['expected_tool']} → {r['actual_tool']}")
            print(f"   Success: {r['expected_success']} → {r['actual_success']}")
            if r["requires_confirmation"]:
                conf_status = "✓" if r["got_confirmation"] else "✗"
                print(f"   Confirmation: Required ({conf_status} Got)")
            print(f"   Duration: {r['duration_ms']}ms")
            if r["error"]:
                print(f"   Error: {r['error']}")
            if r["notes"]:
                print(f"   Notes: {r['notes']}")

        # Save to JSON
        output_file = "test_results_v2.json"
        with open(output_file, "w") as f:
            json.dump({
                "summary": {
                    "total": total,
                    "passed": passed,
                    "failed": failed,
                    "pass_rate": f"{passed/total*100:.1f}%",
                    "total_time": f"{total_time:.2f}s",
                    "avg_time": f"{total_time/total:.2f}s"
                },
                "categories": categories,
                "results": self.results
            }, f, indent=2)

        print(f"\n💾 Detailed results saved to: {output_file}")
        print("="*80 + "\n")


async def test_agent_query(query: str, session_id: str) -> Dict[str, Any]:
    """Send a query to the agent and return the response."""
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


async def run_tests(cleanup_after: bool = True):
    """Run all test cases and generate report."""
    # Setup database before tests
    print("\n" + "="*80)
    print("PREPARING DATABASE FOR TESTING")
    print("="*80)

    cleanup = DatabaseCleanup()
    cleanup.before_tests()

    logger = TestLogger()

    print("\n" + "="*80)
    print("RUNNING COMPREHENSIVE TOOL TESTS")
    print("="*80)
    print(f"\n🚀 Starting tests...")
    print(f"   Testing {len(TEST_CASES)} queries across all 9 tools")
    print(f"   Endpoint: {AGENT_ENDPOINT}\n")

    for i, test_case in enumerate(TEST_CASES, 1):
        print(f"[{i}/{len(TEST_CASES)}] Testing: {test_case['query'][:60]}...")

        session_id = f"test-{test_case['id']}-{int(time.time())}"

        try:
            start = time.time()
            response = await test_agent_query(test_case["query"], session_id)
            duration = time.time() - start

            # Determine success
            if test_case.get("requires_confirmation"):
                # For high-risk actions, success = got confirmation prompt
                success = response.get("requires_confirmation", False)
                notes = "Confirmation flow triggered as expected" if success else "Expected confirmation prompt"
            else:
                # For normal actions, success = execution_success
                success = response.get("execution_success", False)

                # Special case: If we EXPECT failure and we GET an error, that's correct
                if not test_case["expected_success"] and response.get("error"):
                    success = False
                    notes = f"Expected error occurred: {response.get('error')[:50]}"
                else:
                    notes = ""

            logger.log_test(test_case, response, duration, success, notes)

        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}" if str(e) else type(e).__name__
            logger.log_test(test_case, {"error": error_msg}, 0, False, f"Exception: {error_msg}")
            print(f"   ❌ Error: {error_msg}")

        # Small delay between tests
        await asyncio.sleep(0.5)

    # Print summary
    logger.print_summary()

    # Cleanup after tests (optional)
    if cleanup_after:
        print("\n" + "="*80)
        print("CLEANING UP AFTER TESTS")
        print("="*80)
        cleanup.after_tests()
    else:
        print("\n⚠️  Skipping cleanup - test data remains in database")


if __name__ == "__main__":
    print("\n" + "="*80)
    print("MOVI TRANSPORT AGENT - COMPREHENSIVE TOOL TESTING SUITE v2")
    print("="*80)
    print("\nThis test suite covers:")
    print("  • All 9 tool functions")
    print("  • 20 different query variations")
    print("  • Read, Create, and Delete operations")
    print("  • Static and Dynamic asset management")
    print("  • Consequence checking and confirmation flow")
    print("  • Edge cases and error handling")
    print("\nIMPROVEMENTS in v2:")
    print("  • Automatic database cleanup before tests")
    print("  • Test data setup for reliable execution")
    print("  • Optional cleanup after tests (use --no-cleanup-after to skip)")
    print("  • Better error reporting")
    print("\n" + "="*80 + "\n")

    # Check for --no-cleanup-after flag
    cleanup_after = "--no-cleanup-after" not in sys.argv

    # Run tests
    asyncio.run(run_tests(cleanup_after=cleanup_after))
