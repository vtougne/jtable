#!/usr/bin/env python3
"""Simple test to verify completion suggestions work"""

import sys
sys.path.insert(0, '/home/vince/repos/jtable/jtable')

import Apps

# Test that we can get the list
apps = Apps.AppsModule().list_all()

print("=== Tab Completion Test ===\n")
print(f"Total apps/filters available: {len(apps)}\n")

# Test filtering
print("Completions for 'to':")
for app in [a for a in apps if a.startswith('to')]:
    print(f"  - {app}")

print("\nCompletions for 'upp':")
for app in [a for a in apps if a.startswith('upp')]:
    print(f"  - {app}")

print("\nFirst 10 completions (all):")
for app in apps[:10]:
    print(f"  - {app}")

print(f"\n... and {len(apps) - 10} more")

print("\n=== How to enable in your shell ===")
print("\n1. Run this command:")
print("   eval \"$(register-python-argcomplete /home/vince/repos/jtable/jtable/cli_parser.py)\"")
print("\n2. Then test with:")
print("   cd /home/vince/repos/jtable/jtable")
print("   ./cli_parser.py to<TAB>")
print("\n3. To make permanent, add to ~/.bashrc:")
print("   echo 'eval \"$(register-python-argcomplete /home/vince/repos/jtable/jtable/cli_parser.py)\"' >> ~/.bashrc")
