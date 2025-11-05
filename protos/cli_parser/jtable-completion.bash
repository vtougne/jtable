#!/bin/bash



SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Global cleanup function for Ctrl+C
_jtable_sigint_handler() {
    # Clean up F4 binding on Ctrl+C
    bind -r '\eOS' 2>/dev/null || true
}

# Set up global SIGINT trap
trap '_jtable_sigint_handler' SIGINT

# Function to get available apps from Python
_jtable_get_apps() {
    # Call Python to get the list from Apps.AppsModule().list_all()
    python3 -c "
import sys
sys.path.insert(0, '$SCRIPT_DIR')
import Apps
print(' '.join(Apps.AppsModule().list_all()[0:9]))
" 2>/dev/null
# bind -r '\eOS'
}

_preview() {
    _swicth_secondary_screen
    tee <<EOF
Hello $1
hostname    os     cost    state        env
----------  -----  ------  -----------  -----
host_1      linux  5000    alive        qua
host_2      linux  5000    alive        qua
host_3      linux          unreachable  qua
EOF

    echo ""

    read -n 1 -s -r -p "Press any key to exit preview..."

    _back_primary_scrreen

    # Clean up F4 binding after preview is done
    bind -r '\eOS' 2>/dev/null || true
}

_swicth_secondary_screen() {
    tput smcup
}

_back_primary_scrreen() {
    tput rmcup
}

# Main completion function
_jtable_complete() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    # Clean up any previous F4 binding first
    bind -r '\eOS' 2>/dev/null || true

    # Set up F4 key to show preview
    bind -x '"\eOS":"_preview $LOGNAME"'

    opts=$(_jtable_get_apps)

    COMPREPLY=( $(compgen -W "${opts}" -- "${cur}") )
    return 0
}

# Register completion for cli_parser.py
complete -F _jtable_complete cli_parser.py
complete -F _jtable_complete ./cli_parser.py

# Also register for common variations
complete -F _jtable_complete python3\ cli_parser.py
complete -F _jtable_complete python\ cli_parser.py

echo "jtable bash completion loaded (${COMP_WORDS[0]:-cli_parser.py})"
