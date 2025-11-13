# Test Suite Documentation

## Overview

Comprehensive testing suite for the Movi Transport Agent with proper test isolation and database cleanup.

## Files

- **test_all_tools.py** - Original test suite (v1) - May fail due to database pollution
- **test_all_tools_v2.py** - Improved test suite with automatic cleanup
- **test_cleanup.py** - Database cleanup utility for test isolation
- **README.md** - This file

## Problem Analysis

### Original Test Failures (v1)

The original test suite had 5 failures out of 20 tests (75% pass rate):

#### Test #11-14: CREATE - Static (4 failures)
**Problem**: Database pollution from previous test runs
- Stops "Odeon Circle" & "MG Road Metro" already existed
- Paths "Tech-Loop" & "Metro-Route" already existed
- Tests failed with "already exists" errors

**Root Cause**: No cleanup between test runs, causing duplicate entry violations

#### Test #17: DELETE - High Risk (1 failure)
**Problem**: Missing test data setup
- Trip "Hollilux - BTS - 17:00" exists but had NO vehicle assigned
- Test expected to remove a vehicle that didn't exist
- Failed with "No vehicle assigned" error

**Root Cause**: Test data not properly initialized before test execution

### Test Interdependencies

- Test #18 passed because Test #9 assigned a vehicle to trip 1
- Tests are not isolated - they depend on execution order
- This creates brittle tests that fail when run in different orders

## Solutions

### 1. Database Cleanup Utility (`test_cleanup.py`)

Provides three modes:

```bash
# Before tests - Clean old data and setup fresh test data
python tests/test_cleanup.py before

# After tests - Clean up test artifacts
python tests/test_cleanup.py after

# Just setup test data without cleaning
python tests/test_cleanup.py setup

# Full reset (interactive)
python tests/test_cleanup.py full
```

**Features**:
- Removes test-created stops (Odeon Circle, MG Road Metro)
- Removes test-created paths (Tech-Loop, Metro-Route)
- Removes test-created routes (recent additions)
- Removes test-created deployments (last hour)
- Sets up required test data (assigns vehicle to trip 6)

### 2. Improved Test Suite (`test_all_tools_v2.py`)

**Improvements**:
- Automatic database cleanup before tests
- Test data setup for reliable execution
- Optional cleanup after tests
- Better error reporting
- Proper test isolation

**Usage**:
```bash
# Run with cleanup after tests (default)
python tests/test_all_tools_v2.py

# Run without cleanup (for debugging)
python tests/test_all_tools_v2.py --no-cleanup-after
```

## Expected Results

With the improved test suite (v2), all 20 tests should pass:

- ✅ READ - Dynamic (4/4) - 100%
- ✅ READ - Static (4/4) - 100%
- ✅ CREATE - Dynamic (2/2) - 100%
- ✅ CREATE - Static (6/6) - 100%
- ✅ DELETE - High Risk (2/2) - 100%
- ✅ EDGE CASE - Not Found (1/1) - 100%
- ✅ EDGE CASE - Complex Query (1/1) - 100%

**Target Pass Rate**: 100% (20/20 tests)

## Database State Management

### Before Tests
1. Remove all test-created entities from previous runs
2. Assign vehicle to trip 6 for Test #17
3. Ensure clean slate for CREATE operations

### After Tests (Optional)
1. Remove all test-created entities
2. Restore database to original state
3. Prevent pollution for next test run

### Test Data Setup
- Trip 6 ("Hollilux - BTS - 17:00") gets a vehicle assigned
- Unassigned vehicles remain available for Test #9 and #10
- No interference with existing production-like data

## Quick Start

### Option 1: Run Improved Test Suite (Recommended)
```bash
cd /Users/radhikakulkarni/Downloads/30days_challenge/assignment_for_moveinsync/movi-transport-agent/backend

# Make sure backend is running
# In another terminal: ./venv/bin/python -m uvicorn main:app --reload

# Run tests with automatic cleanup
python tests/test_all_tools_v2.py
```

### Option 2: Manual Cleanup + Original Tests
```bash
cd /Users/radhikakulkarni/Downloads/30days_challenge/assignment_for_moveinsync/movi-transport-agent/backend

# Clean database first
python tests/test_cleanup.py before

# Run original tests
python tests/test_all_tools.py

# Clean up after
python tests/test_cleanup.py after
```

## Troubleshooting

### Tests Still Failing After Cleanup?

**Check backend is running**:
```bash
curl http://localhost:8000/api/v1/trips
```

**Check database state**:
```bash
sqlite3 database/transport.db "SELECT * FROM stops WHERE name IN ('Odeon Circle', 'MG Road Metro');"
sqlite3 database/transport.db "SELECT * FROM paths WHERE path_name IN ('Tech-Loop', 'Metro-Route');"
sqlite3 database/transport.db "SELECT dt.trip_id, dt.display_name, v.license_plate FROM daily_trips dt LEFT JOIN deployments d ON dt.trip_id = d.trip_id LEFT JOIN vehicles v ON d.vehicle_id = v.vehicle_id WHERE dt.trip_id = 6;"
```

**Re-run cleanup**:
```bash
python tests/test_cleanup.py before
```

### Test Timeout Errors?

Tests have 90-second timeout for LLM responses. If still timing out:
1. Check OpenRouter API key is valid
2. Check Claude Sonnet 4.5 availability
3. Check network connectivity

### Database Locked Errors?

```bash
# Kill any hanging processes
pkill -f uvicorn

# Wait a moment
sleep 2

# Restart backend
./venv/bin/python -m uvicorn main:app --reload
```

## Best Practices

1. **Always clean before tests**: Run `test_cleanup.py before` before manual test runs
2. **Use v2 suite for CI/CD**: Automatic cleanup ensures reliable results
3. **Debug with --no-cleanup-after**: Inspect database state after failures
4. **Check test results JSON**: Detailed metrics saved to `test_results_v2.json`

## Test Categories Explained

### READ - Dynamic
Tests that query current system state (vehicles, trips, deployments)
- Can change between test runs
- Expected to always succeed with current data

### READ - Static
Tests that query static configuration (stops, paths, routes)
- Should be stable across test runs
- Tests data relationships and joins

### CREATE - Dynamic
Tests that modify system state (assign vehicles, create deployments)
- Can be run multiple times if properly cleaned
- Test #9 and #10 can overwrite previous assignments

### CREATE - Static
Tests that create configuration entities (stops, paths, routes)
- Require cleanup to run successfully
- Test duplicate detection logic

### DELETE - High Risk
Tests that remove critical assignments
- Should trigger confirmation flow
- Test consequence checking and tribal knowledge

### EDGE CASES
Tests error handling and edge conditions
- Not Found: Tests missing entity handling
- Complex Query: Tests natural language understanding

## Key Insights

1. **Test Isolation Critical**: Tests must not depend on each other's side effects
2. **Database Cleanup Required**: CREATE operations need fresh state
3. **Test Data Setup**: High-risk operations need proper initial state
4. **Idempotency**: Tests should be runnable multiple times
5. **Cleanup After**: Prevents pollution for next test run

## Future Improvements

1. **Test Database**: Use separate test.db instead of production database
2. **Transactions**: Wrap each test in a transaction that rolls back
3. **Fixtures**: Create reusable test data fixtures
4. **Parallel Tests**: Run independent test categories in parallel
5. **Coverage**: Add integration tests for full agent flow
