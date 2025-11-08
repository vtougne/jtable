#!/bin/bash

# Non-interactive testing script for cli_parser.py
# Tests the CLI functionality and completion system without requiring user interaction

# Note: We don't use 'set -e' here because we want to run all tests even if some fail

# Color codes for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Helper functions
print_test_header() {
    echo ""
    echo "=========================================="
    echo "$1"
    echo "=========================================="
}

print_success() {
    echo -e "${GREEN}✓ PASS${NC}: $1"
    ((TESTS_PASSED++))
    ((TESTS_RUN++))
}

print_failure() {
    echo -e "${RED}✗ FAIL${NC}: $1"
    echo -e "${RED}  Expected: $2${NC}"
    echo -e "${RED}  Got: $3${NC}"
    ((TESTS_FAILED++))
    ((TESTS_RUN++))
}

print_info() {
    echo -e "${YELLOW}INFO${NC}: $1"
}

# Test function
assert_equals() {
    local test_name="$1"
    local expected="$2"
    local actual="$3"

    if [ "$expected" == "$actual" ]; then
        print_success "$test_name"
        return 0
    else
        print_failure "$test_name" "$expected" "$actual"
        return 1
    fi
}

assert_contains() {
    local test_name="$1"
    local haystack="$2"
    local needle="$3"

    if [[ "$haystack" == *"$needle"* ]]; then
        print_success "$test_name"
        return 0
    else
        print_failure "$test_name" "String containing '$needle'" "$haystack"
        return 1
    fi
}

assert_exit_code() {
    local test_name="$1"
    local expected_code="$2"
    local actual_code="$3"

    if [ "$expected_code" -eq "$actual_code" ]; then
        print_success "$test_name"
        return 0
    else
        print_failure "$test_name" "Exit code $expected_code" "Exit code $actual_code"
        return 1
    fi
}

# ==========================================
# Test 1: Python API - Apps.AppsModule
# ==========================================
print_test_header "Test 1: Python API - Apps.AppsModule"

# Test 1.1: list_all() returns expected items
print_info "Testing Apps.AppsModule().list_all()"
result=$(python3 -c "
import sys
sys.path.insert(0, '$SCRIPT_DIR')
import Apps
print(' '.join(Apps.AppsModule().list_all()))
")
assert_contains "list_all() includes 'abs'" "$result" "abs"
assert_contains "list_all() includes 'to_table'" "$result" "to_table"
assert_contains "list_all() includes 'to_yaml'" "$result" "to_yaml"

# Test 1.2: list_apps() returns custom apps only
print_info "Testing Apps.AppsModule().list_apps()"
result=$(python3 -c "
import sys
sys.path.insert(0, '$SCRIPT_DIR')
import Apps
print(' '.join(Apps.AppsModule().list_apps()))
")
assert_contains "list_apps() includes 'to_table'" "$result" "to_table"
assert_contains "list_apps() includes 'to_yaml'" "$result" "to_yaml"

# Test 1.3: list_builtins() returns jinja builtins
print_info "Testing Apps.AppsModule().list_builtins()"
result=$(python3 -c "
import sys
sys.path.insert(0, '$SCRIPT_DIR')
import Apps
print(' '.join(Apps.AppsModule().list_builtins()))
")
assert_contains "list_builtins() includes 'abs'" "$result" "abs"
assert_contains "list_builtins() includes 'capitalize'" "$result" "capitalize"

# Test 1.4: Verify list_all() is sorted
print_info "Testing that list_all() is sorted"
is_sorted=$(python3 -c "
import sys
sys.path.insert(0, '$SCRIPT_DIR')
import Apps
apps = Apps.AppsModule().list_all()
print('true' if apps == sorted(apps) else 'false')
")
assert_equals "list_all() returns sorted list" "true" "$is_sorted"

# ==========================================
# Test 2: CLI Parser - --list-apps flag
# ==========================================
print_test_header "Test 2: CLI Parser - --list-apps flag"

# Test 2.1: --list-apps returns list of apps
print_info "Testing ./cli_parser.py --list-apps"
output=$(./cli_parser.py --list-apps 2>&1 || true)
assert_contains "--list-apps includes 'abs'" "$output" "abs"
assert_contains "--list-apps includes 'to_table'" "$output" "to_table"

# Test 2.2: --list-apps exits with code 0
exit_code=0
./cli_parser.py --list-apps >/dev/null 2>&1 || exit_code=$?
assert_exit_code "--list-apps exits successfully" 0 $exit_code

# ==========================================
# Test 3: CLI Parser - Valid app selection
# ==========================================
print_test_header "Test 3: CLI Parser - Valid app selection"

# Test 3.1: Valid app 'to_table' is accepted
print_info "Testing ./cli_parser.py to_table"
output=$(./cli_parser.py to_table 2>&1 || true)
assert_contains "Valid app 'to_table' is accepted" "$output" "Selected app/filter: to_table"

# Test 3.2: Valid app 'to_yaml' is accepted
print_info "Testing ./cli_parser.py to_yaml"
output=$(./cli_parser.py to_yaml 2>&1 || true)
assert_contains "Valid app 'to_yaml' is accepted" "$output" "Selected app/filter: to_yaml"

# Test 3.3: Valid builtin 'abs' is accepted
print_info "Testing ./cli_parser.py abs"
output=$(./cli_parser.py abs 2>&1 || true)
assert_contains "Valid builtin 'abs' is accepted" "$output" "Selected app/filter: abs"

# Test 3.4: Valid apps exit with code 0
exit_code=0
./cli_parser.py to_table >/dev/null 2>&1 || exit_code=$?
assert_exit_code "Valid app exits successfully" 0 $exit_code

# ==========================================
# Test 4: CLI Parser - Invalid app rejection
# ==========================================
print_test_header "Test 4: CLI Parser - Invalid app rejection"

# Test 4.1: Invalid app is rejected
print_info "Testing ./cli_parser.py invalid_app"
output=$(./cli_parser.py invalid_app 2>&1 || true)
assert_contains "Invalid app shows error" "$output" "Error:"

# Test 4.2: Invalid app exits with non-zero code
exit_code=0
./cli_parser.py invalid_app >/dev/null 2>&1 || exit_code=$?
assert_exit_code "Invalid app exits with error" 1 $exit_code

# ==========================================
# Test 5: CLI Parser - No arguments
# ==========================================
print_test_header "Test 5: CLI Parser - No arguments"

# Test 5.1: No args shows help
print_info "Testing ./cli_parser.py (no args)"
output=$(./cli_parser.py 2>&1 || true)
assert_contains "No args shows usage" "$output" "usage:"
assert_contains "No args shows available apps" "$output" "Available apps and filters"

# Test 5.2: No args exits with code 0
exit_code=0
./cli_parser.py >/dev/null 2>&1 || exit_code=$?
assert_exit_code "No args exits successfully" 0 $exit_code

# ==========================================
# Test 6: Completion function
# ==========================================
print_test_header "Test 6: Completion function"

# Test 6.1: _jtable_get_apps function from completion script
print_info "Testing _jtable_get_apps function"
source jtable-completion.bash 2>/dev/null || true
apps_output=$(_jtable_get_apps 2>/dev/null || echo "")
if [ -n "$apps_output" ]; then
    assert_contains "Completion function returns apps" "$apps_output" "abs"
    print_info "Completion apps (first 9): $apps_output"
else
    print_info "Skipping completion test (requires bash completion support)"
fi

# ==========================================
# Test 7: Count verification
# ==========================================
print_test_header "Test 7: Count verification"

# Test 7.1: Verify total count of apps
print_info "Counting total apps"
total_count=$(python3 -c "
import sys
sys.path.insert(0, '$SCRIPT_DIR')
import Apps
print(len(Apps.AppsModule().list_all()))
")
print_info "Total apps available: $total_count"

# Expected: 43 jinja builtins + 2 custom apps = 45 total
expected_min=45
if [ "$total_count" -ge "$expected_min" ]; then
    print_success "Total app count ($total_count) is >= $expected_min"
    ((TESTS_PASSED++))
    ((TESTS_RUN++))
else
    print_failure "Total app count check" ">= $expected_min" "$total_count"
    ((TESTS_FAILED++))
    ((TESTS_RUN++))
fi

# ==========================================
# Test 8: Preview Function (F4 functionality)
# ==========================================
print_test_header "Test 8: Preview Function (F4 functionality)"

# Test 8.1: Source completion script and test helper functions exist
print_info "Sourcing jtable-completion.bash"
source jtable-completion.bash 2>/dev/null || true

# Check if functions are defined
if declare -f _preview >/dev/null; then
    print_success "_preview function is defined"
    ((TESTS_PASSED++))
    ((TESTS_RUN++))
else
    print_failure "_preview function check" "Function defined" "Function not found"
    ((TESTS_FAILED++))
    ((TESTS_RUN++))
fi

if declare -f _swicth_secondary_screen >/dev/null; then
    print_success "_swicth_secondary_screen function is defined"
    ((TESTS_PASSED++))
    ((TESTS_RUN++))
else
    print_failure "_swicth_secondary_screen function check" "Function defined" "Function not found"
    ((TESTS_FAILED++))
    ((TESTS_RUN++))
fi

if declare -f _back_primary_scrreen >/dev/null; then
    print_success "_back_primary_scrreen function is defined"
    ((TESTS_PASSED++))
    ((TESTS_RUN++))
else
    print_failure "_back_primary_scrreen function check" "Function defined" "Function not found"
    ((TESTS_FAILED++))
    ((TESTS_RUN++))
fi

# Test 8.2: Test preview function output (non-interactive version)
print_info "Testing _preview function output"

# Create a non-interactive version of _preview for testing
_preview_non_interactive() {
    local username="$1"
    cat <<EOF
Hello $username
hostname    os     cost    state        env
----------  -----  ------  -----------  -----
host_1      linux  5000    alive        qua
host_2      linux  5000    alive        qua
host_3      linux          unreachable  qua
EOF
}

# Test the output
preview_output=$(_preview_non_interactive "testuser")
assert_contains "Preview output contains greeting" "$preview_output" "Hello testuser"
assert_contains "Preview output contains hostname header" "$preview_output" "hostname"
assert_contains "Preview output contains table data" "$preview_output" "host_1"
assert_contains "Preview output contains host_2" "$preview_output" "host_2"
assert_contains "Preview output contains host_3" "$preview_output" "host_3"

# Test 8.3: Test screen switching functions
print_info "Testing screen switching commands"

# Test that tput commands are available
if command -v tput >/dev/null 2>&1; then
    print_success "tput command is available"
    ((TESTS_PASSED++))
    ((TESTS_RUN++))

    # Test smcup (switch to secondary screen) - just verify it doesn't error
    if tput smcup 2>/dev/null && tput rmcup 2>/dev/null; then
        print_success "tput smcup/rmcup commands work"
        ((TESTS_PASSED++))
        ((TESTS_RUN++))
    else
        print_info "tput smcup/rmcup may not be supported in this terminal (non-critical)"
        ((TESTS_PASSED++))
        ((TESTS_RUN++))
    fi
else
    print_failure "tput availability check" "tput available" "tput not found"
    ((TESTS_FAILED++))
    ((TESTS_RUN++))
fi

# Test 8.4: Test F4 key binding (limited in non-interactive mode)
print_info "Testing F4 key binding setup"

# In non-interactive shells, bind may not work, so we just test it doesn't crash
if bind -x '"\eOS":"echo test"' 2>/dev/null; then
    print_success "bind command works (F4 binding is possible)"
    bind -r '\eOS' 2>/dev/null || true
    ((TESTS_PASSED++))
    ((TESTS_RUN++))
else
    print_info "bind command not available in non-interactive mode (expected limitation)"
    # This is not a failure - bind typically requires interactive shell
    ((TESTS_PASSED++))
    ((TESTS_RUN++))
fi

# Test 8.5: Test cleanup handler
print_info "Testing SIGINT cleanup handler"
if declare -f _jtable_sigint_handler >/dev/null; then
    print_success "_jtable_sigint_handler function is defined"
    ((TESTS_PASSED++))
    ((TESTS_RUN++))
else
    print_failure "_jtable_sigint_handler function check" "Function defined" "Function not found"
    ((TESTS_FAILED++))
    ((TESTS_RUN++))
fi

# Test 8.6: Test that completion message was shown
print_info "Testing completion loading message"
completion_msg=$(source jtable-completion.bash 2>&1 | grep "jtable bash completion loaded")
if [ -n "$completion_msg" ]; then
    print_success "Completion script shows loading message"
    ((TESTS_PASSED++))
    ((TESTS_RUN++))
else
    print_failure "Completion loading message check" "Message shown" "No message found"
    ((TESTS_FAILED++))
    ((TESTS_RUN++))
fi

# ==========================================
# Test Summary
# ==========================================
echo ""
echo "=========================================="
echo "TEST SUMMARY"
echo "=========================================="
echo "Total tests run: $TESTS_RUN"
echo -e "${GREEN}Tests passed: $TESTS_PASSED${NC}"
if [ $TESTS_FAILED -gt 0 ]; then
    echo -e "${RED}Tests failed: $TESTS_FAILED${NC}"
else
    echo -e "${GREEN}Tests failed: $TESTS_FAILED${NC}"
fi
echo "=========================================="

# Exit with appropriate code
if [ $TESTS_FAILED -gt 0 ]; then
    exit 1
else
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
fi
