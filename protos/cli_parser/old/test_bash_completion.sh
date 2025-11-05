#!/bin/bash
cd /home/vince/repos/jtable/jtable

echo "=== Testing Native Bash Completion ==="
echo ""

# Source the completion script
source ./jtable-completion.bash

echo ""
echo "1. Testing _jtable_get_apps function:"
apps=$(_jtable_get_apps)
echo "   Found: $(echo $apps | wc -w) apps/filters"
echo "   First 10: $(echo $apps | tr ' ' '\n' | head -10 | tr '\n' ' ')"
echo ""

echo "2. Testing completion with 'to' prefix:"
COMP_WORDS=(cli_parser.py to)
COMP_CWORD=1
_jtable_complete
echo "   Completions: ${COMPREPLY[@]}"
echo ""

echo "3. Testing completion with 'upp' prefix:"
COMP_WORDS=(cli_parser.py upp)
COMP_CWORD=1
_jtable_complete
echo "   Completions: ${COMPREPLY[@]}"
echo ""

echo "4. Testing completion with no prefix:"
COMP_WORDS=(cli_parser.py "")
COMP_CWORD=1
_jtable_complete
echo "   Total completions: ${#COMPREPLY[@]}"
echo "   First 10: ${COMPREPLY[@]:0:10}"
echo ""

echo "=== Test Complete ==="
