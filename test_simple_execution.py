#!/usr/bin/env python3
"""
Simple test for action execution.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'jtable'))

from actions import LoadYamlAction, ActionContext

def test_simple_execution():
    """Test simple action execution."""
    print("Testing simple action execution...")
    
    context = ActionContext()
    action = LoadYamlAction()
    
    try:
        result = action.execute(
            context, 
            file='doc/examples/host_list_of_dict.yml',
            dataset_name='hosts'
        )
        
        print("✓ Load YAML action executed successfully")
        print(f"✓ Loaded {len(result)} items")
        print(f"✓ First item: {result[0] if result else 'None'}")
        
        # Check if data is stored in context
        stored = context.get_dataset('hosts')
        print(f"✓ Data stored in context: {len(stored)} items")
        
        return True
    except Exception as e:
        print(f"✗ Execution failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_simple_execution()