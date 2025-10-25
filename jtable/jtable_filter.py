#!/usr/bin/env python3
import sys
import os
import logging
import logging.config

# Add jtable to path
jtable_path = os.path.dirname(os.path.abspath(__file__))
if jtable_path not in sys.path:
    sys.path.insert(0, jtable_path)

# Import logging configuration
from logger import logging_config

# Import Player class
from player import Player

# Import Plugin for environment variable access
from functions import Plugin


def build_filter_expression(args):
    """
    Build a Jinja2 filter expression from parsed arguments.

    This function converts the CLI filter chain into a Jinja template expression.
    For example:
        ['to_table', '-p', 'hosts', '-s', 'hostname,os,state']
    becomes:
        "to_table(path='hosts', select=['hostname', 'os', 'state'])"

    Args:
        args (list): List of argument strings representing the filter and its options

    Returns:
        str: Jinja filter expression
    """
    if not args:
        return ""

    filter_name = args[0]
    filter_args = []
    filter_kwargs = {}

    i = 1
    while i < len(args):
        arg = args[i]

        if arg.startswith('-'):
            # It's an option
            option_name = arg.lstrip('-')

            # Map common short options to their full names
            option_mapping = {
                'p': 'path',
                's': 'select',
                'us': 'unselect',
                'w': 'when',
                'f': 'format',
            }

            full_option = option_mapping.get(option_name, option_name)

            # Get the value (next argument)
            if i + 1 < len(args) and not args[i + 1].startswith('-'):
                value = args[i + 1]
                i += 1

                # Handle comma-separated values (like select fields)
                if ',' in value and full_option in ['select', 'unselect']:
                    # Convert to list
                    filter_kwargs[full_option] = [v.strip() for v in value.split(',')]
                elif full_option == 'path':
                    # Auto-append {} to path if not already present
                    # This matches the behavior of the old jtable CLI
                    import re
                    expr_end_by_braces = re.sub('.*({).*(})$', r'\1\2', value)
                    if expr_end_by_braces != "{}":
                        value = value + "{}"
                    filter_kwargs[full_option] = value
                else:
                    filter_kwargs[full_option] = value
            else:
                # Boolean flag
                filter_kwargs[full_option] = True

        i += 1

    # Build the filter expression
    params = []

    # Add kwargs
    for key, value in filter_kwargs.items():
        if isinstance(value, list):
            # For select/unselect, join with comma and pass as string
            # (to_table expects select as a comma-separated string, not a list)
            if key in ['select', 'unselect']:
                formatted_value = ','.join(value)
                params.append(f'{key}="{formatted_value}"')
            else:
                # Format as Python list for other parameters
                formatted_list = '[' + ', '.join([f'"{v}"' for v in value]) + ']'
                params.append(f'{key}={formatted_list}')
        elif isinstance(value, bool):
            params.append(f'{key}={str(value)}')
        elif isinstance(value, str):
            params.append(f'{key}="{value}"')
        else:
            params.append(f'{key}={value}')

    if params:
        return f"{filter_name}({', '.join(params)})"
    else:
        return filter_name


def parse_filter_chain(argv):
    """
    Parse command-line arguments to identify module and filter chain.

    This function processes the argv to extract:
    1. Optional initial module (like 'load_json <file>')
    2. Chain of filters with their options

    Returns:
        tuple: (module_expr, filter_exprs)
            module_expr: Initial module expression or None if stdin is used
            filter_exprs: List of filter expressions
    """
    module_expr = None
    filter_exprs = []
    current_filter = []

    # Known modules that take a filename argument
    known_modules = ['load_json', 'load_yaml']

    # Known filters
    known_filters = ['from_json', 'from_yaml', 'to_table', 'to_json', 'to_yaml',
                     'to_nice_json', 'to_nice_yaml', 'from_json_or_yaml']

    i = 0

    # Check if first argument is a module
    if i < len(argv) and argv[i] in known_modules:
        module_name = argv[i]
        i += 1

        # Get the filename argument
        if i < len(argv) and not argv[i].startswith('-') and argv[i] not in known_filters:
            filename = argv[i]
            module_expr = f'{module_name}("{filename}")'
            i += 1
        else:
            # Module without filename - error
            logging.error(f"Module '{module_name}' requires a filename argument")
            sys.exit(1)

    # Parse filters
    while i < len(argv):
        arg = argv[i]

        if arg in known_filters:
            # Save previous filter if any
            if current_filter:
                filter_exprs.append(build_filter_expression(current_filter))

            # Start new filter
            current_filter = [arg]
        elif arg.startswith('-') or (current_filter and not arg in known_filters):
            # Option for current filter
            current_filter.append(arg)
        else:
            logging.error(f"Unexpected argument: {arg}")
            sys.exit(1)

        i += 1

    # Save last filter
    if current_filter:
        filter_exprs.append(build_filter_expression(current_filter))

    return module_expr, filter_exprs


def main():
    """Main entry point for jtable-filter CLI"""
    # Configure logging (simple version for now)
    logging_config['handlers']['console_stderr']['level'] = 'WARNING'
    logging.config.dictConfig(logging_config)

    # Check for help
    if '--help' in sys.argv or '-h' in sys.argv or len(sys.argv) == 1:
        print("""jtable-filter - Chain filters for data transformation

Usage:
    # With module (loading from file)
    jtable-filter <module> <module_args> [filter <filter_options>]...

    # From stdin (piped data)
    cat data.json | jtable-filter <filter> [filter_options] [filter <filter_options>]...

Modules:
    load_json <file>    Load JSON file
    load_yaml <file>    Load YAML file

Filters:
    from_json           Parse JSON string
    from_yaml           Parse YAML string
    to_table            Render as table
        -p, --path      Path in data structure
        -s, --select    Comma-separated list of columns to select
        -us, --unselect Comma-separated list of columns to exclude
        -w, --when      Filter condition
        -f, --format    Output format (simple, github, html, etc.)
    to_json             Convert to JSON
    to_yaml             Convert to YAML
    to_nice_json        Convert to nicely formatted JSON
    to_nice_yaml        Convert to nicely formatted YAML

Examples:
    # Load JSON file and display as table
    jtable-filter load_json data.json to_table -p hosts -s hostname,os,state

    # From stdin with filter chain
    cat data.json | jtable-filter from_json to_table -p hosts

    # Multiple filters
    cat data.yml | jtable-filter from_yaml to_table -s name,value to_json

Options:
    -h, --help         Show this help message
    -v, --verbose      Increase verbosity
    --debug            Enable debug mode
""")
        sys.exit(0)

    # Parse arguments
    verbose = '--verbose' in sys.argv or '-v' in sys.argv
    debug = '--debug' in sys.argv

    # Remove options from argv
    argv = [arg for arg in sys.argv[1:] if arg not in ['--verbose', '-v', '--debug']]

    if verbose:
        logging_config['handlers']['console_stderr']['level'] = 'INFO'
    if debug:
        logging_config['handlers']['console_stderr']['level'] = 'DEBUG'
        logging_config['formatters']['my_formatter']['format'] = \
            '%(asctime)s (%(lineno)s) %(class_name)s.%(parent_function)-16s | %(levelname)s %(message)s'

    logging.config.dictConfig(logging_config)

    # Check for stdin data
    stdin_data = None
    if not sys.stdin.isatty():
        stdin_data = sys.stdin.read()
        logging.info("Read data from stdin")

    # Parse the filter chain
    module_expr, filter_exprs = parse_filter_chain(argv)

    logging.info(f"Module expression: {module_expr}")
    logging.info(f"Filter expressions: {filter_exprs}")

    # Build the template expression
    if module_expr:
        # Start with module
        template_expr = module_expr
    else:
        # Start with stdin
        if stdin_data is None:
            logging.error("No input data provided. Either use a module (load_json, load_yaml) or pipe data via stdin.")
            sys.exit(1)
        template_expr = "stdin"

    # Add filters
    for filter_expr in filter_exprs:
        template_expr += f" | {filter_expr}"

    # Wrap in Jinja template syntax
    template = f"{{{{ {template_expr} }}}}"

    logging.info(f"Generated template: {template}")

    # Build in-memory playbook
    playbook = {
        'stdout': template,
        'vars': {}
    }

    # Create and execute player
    try:
        player = Player(
            playbook_dict=playbook,
            variables={},
            stdin_data=stdin_data
        )
        output = player.execute()
        print(output)
    except KeyboardInterrupt:
        sys.exit(1)
    except Exception as error:
        logging.error(f"Failed to execute filter chain: {error}")
        if debug:
            raise
        sys.exit(1)


if __name__ == '__main__':
    main()
