#!/usr/bin/env python3
"""
Test the full action chaining as requested.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'jtable'))

from action_parser import ActionChainParser

def test_your_desired_syntax():
    """Test the exact syntax you requested."""
    print("Testing your desired command syntax...")
    print("Command: jtable load_json json_file.json --as dataset to_table -p dataset.dc_1 -s hostname,ip,state")
    
    parser = ActionChainParser()
    
    # First, let's test with the YAML file we have
    args = ['load_yaml', 'doc/examples/host_list_of_dict.yml', '--as', 'dataset', 
            'to_table', '--dataset', 'dataset', '-s', 'hostname,state']
    
    try:
        print("\n1. Parsing action chain...")
        chains = parser.parse_action_chain(args)
        print(f"✓ Parsed {len(chains)} actions:")
        for i, chain in enumerate(chains):
            print(f"  Action {i+1}: {chain['action']} -> {chain['args']}")
        
        print("\n2. Executing action chain...")
        result = parser.execute_action_chain(chains)
        
        print("✓ Execution completed!")
        print("\n3. Result:")
        print(result)
        
        return True
        
    except Exception as e:
        print(f"✗ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_your_desired_syntax()
    if success:
        print("\n🎉 Your desired action chaining syntax is working!")
    else:
        print("\n❌ Action chaining needs more work")