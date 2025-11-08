#!/bin/bash
# Quick installer for jtable bash completion

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPLETION_SCRIPT="$SCRIPT_DIR/jtable-completion.bash"

echo "=== jtable Bash Completion Installer ==="
echo ""

# Fix line endings if needed
if command -v dos2unix &> /dev/null; then
    dos2unix "$COMPLETION_SCRIPT" 2>/dev/null
else
    sed -i 's/\r$//' "$COMPLETION_SCRIPT" 2>/dev/null
fi

# Detect shell config file
if [ -f "$HOME/.bash_profile" ]; then
    RC_FILE="$HOME/.bash_profile"
elif [ -f "$HOME/.bashrc" ]; then
    RC_FILE="$HOME/.bashrc"
else
    echo "Warning: Could not find ~/.bashrc or ~/.bash_profile"
    RC_FILE="$HOME/.bashrc"
fi

echo "Detected shell config: $RC_FILE"
echo ""

# Check if already installed
if grep -q "jtable-completion.bash" "$RC_FILE" 2>/dev/null; then
    echo "✓ Completion already installed in $RC_FILE"
else
    echo "Installing completion to $RC_FILE..."
    echo "" >> "$RC_FILE"
    echo "# jtable CLI completion" >> "$RC_FILE"
    echo "source $COMPLETION_SCRIPT" >> "$RC_FILE"
    echo "✓ Added to $RC_FILE"
fi

echo ""
echo "=== Installation Complete ==="
echo ""
echo "To activate in current shell:"
echo "  source $COMPLETION_SCRIPT"
echo ""
echo "To test:"
echo "  cd $SCRIPT_DIR"
echo "  ./cli_parser.py to<TAB>"
echo ""
echo "Or restart your shell to activate."
