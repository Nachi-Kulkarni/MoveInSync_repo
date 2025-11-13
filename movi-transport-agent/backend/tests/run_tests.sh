#!/bin/bash

#
# Comprehensive Test Runner for Movi Transport Agent
#
# This script runs the improved test suite with proper database cleanup
#

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Change to backend directory
cd "$(dirname "$0")/.."

echo -e "${BLUE}"
echo "================================================================================"
echo "  MOVI TRANSPORT AGENT - COMPREHENSIVE TEST RUNNER"
echo "================================================================================"
echo -e "${NC}"

# Check if backend is running
echo -e "${YELLOW}Checking if backend is running...${NC}"
if ! curl -s http://localhost:8000/api/v1/trips > /dev/null; then
    echo -e "${RED}❌ Backend is not running!${NC}"
    echo -e "${YELLOW}Please start the backend in another terminal:${NC}"
    echo -e "  cd backend"
    echo -e "  ../venv/bin/python -m uvicorn main:app --reload"
    exit 1
fi
echo -e "${GREEN}✓ Backend is running${NC}\n"

# Clean database and setup test data
echo -e "${YELLOW}Preparing database for testing...${NC}"
python3 tests/test_cleanup.py before
echo ""

# Run improved test suite
echo -e "${YELLOW}Running comprehensive test suite v2...${NC}"
python3 tests/test_all_tools_v2.py

# Check exit code
if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}✅ All tests completed successfully!${NC}"
else
    echo -e "\n${RED}❌ Some tests failed. Check output above for details.${NC}"
    exit 1
fi

echo -e "\n${BLUE}Test results saved to: test_results_v2.json${NC}"
echo -e "${BLUE}For detailed analysis, review the test_results_v2.json file${NC}\n"
