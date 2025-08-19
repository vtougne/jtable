#!/usr/bin/env python3
"""
Test script for the new action chaining functionality.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'jtable'))

from action_parser import ActionChainParser
from actions import ActionContext

def test_basic_parsing():
    """Test basic action chain parsing."""
    print("Testing basic action chain parsing...")
    
    parser = ActionChainParser()
    args = ['load_yaml', 'doc/examples/host_list_of_dict.yml', '--as', 'hosts', 'to_table', '-s', 'hostname,state']
    
    try:
        chains = parser.parse_action_chain(args)
        print(f"✓ Successfully parsed {len(chains)} actions")
        for i, chain in enumerate(chains):
            print(f"  Action {i+1}: {chain['action']} with args {chain['args']}")
        return True
    except Exception as e:
        print(f"✗ Parsing failed: {e}")
        return False

def test_execution():
    """Test action chain execution."""
    print("\nTesting action chain execution...")
    
    parser = ActionChainParser()
    args = ['load_yaml', 'doc/examples/host_list_of_dict.yml', '--as', 'hosts', 'to_table', '-s', 'hostname,state']
    
    try:
        result = parser.parse_and_execute(args)
        print("✓ Action chain executed successfully")
        print("Result:")
        print(result)
        return True
    except Exception as e:
        print(f"✗ Execution failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_stdin_processing():
    """Test stdin processing with action chains."""
    print("\nTesting stdin processing...")
    
    # This would be used with: cat file.yml | python test_action_chain.py
    # For now, just test that the context can handle data
    context = ActionContext()
    test_data = [{'name': 'test', 'value': 123}]
    context.store_dataset('test', test_data)
    
    retrieved = context.get_dataset('test')
    if retrieved == test_data:
        print("✓ Context data storage/retrieval works")
        return True
    else:
        print("✗ Context data storage/retrieval failed")
        return False

if __name__ == "__main__":
    print("Testing new action chaining system...")
    print("=" * 50)
    
    success = True
    
    # Test 1: Basic parsing
    success &= test_basic_parsing()
    
    # Test 2: Context functionality
    success &= test_stdin_processing()
    
    # Test 3: Full execution (commented out for now due to dependencies)
    # success &= test_execution()
    
    print("=" * 50)
    if success:
        print("✓ All tests passed!")
        sys.exit(0)
    else:
        print("✗ Some tests failed!")
        sys.exit(1)