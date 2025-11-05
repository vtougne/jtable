#!/bin/bash
# Test tab completion functionality

# cd /home/vince/repos/jtable/jtable

echo "=== Testing Tab Completion for jtable CLI ==="
echo ""

# Register completion
eval "$(register-python-argcomplete cli_parser.py)"

echo "1. Testing completion with 'to' prefix:"
# Simulate typing: ./cli_parser.py to<TAB>
COMP_WORDS=(./cli_parser.py to)
COMP_CWORD=1
COMP_LINE="./cli_parser.py to"
COMP_POINT=${#COMP_LINE}
_python_argcomplete ./cli_parser.py
echo "   Completions: ${COMPREPLY[@]}"
echo ""

echo "2. Testing completion with 'upp' prefix:"
# Simulate typing: ./cli_parser.py upp<TAB>
COMPREPLY=()
COMP_WORDS=(./cli_parser.py upp)
COMP_CWORD=1
COMP_LINE="./cli_parser.py upp"
COMP_POINT=${#COMP_LINE}
_python_argcomplete ./cli_parser.py
echo "   Completions: ${COMPREPLY[@]}"
echo ""

echo "3. Testing completion with no prefix (all options):"
# Simulate typing: ./cli_parser.py <TAB>
COMPREPLY=()
COMP_WORDS=(./cli_parser.py "")
COMP_CWORD=1
COMP_LINE="./cli_parser.py "
COMP_POINT=${#COMP_LINE}
_python_argcomplete ./cli_parser.py
echo "   Total completions: ${#COMPREPLY[@]}"
echo "   First 10: ${COMPREPLY[@]:0:10}"
echo ""

echo "=== Test Complete ==="
