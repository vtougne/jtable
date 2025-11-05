#!/usr/bin/env python3
"""
CLI parser with tab completion support for jtable apps and filters.
Provides autocomplete for available apps and Jinja built-in filters.
"""

import argparse
import sys

import Apps


def get_available_apps():
    """Returns a list of all available apps and filters for completion."""
    return Apps.AppsModule().list_all()


def app_completer(prefix, parsed_args, **kwargs):
    """Custom completer function for app names."""
    return get_available_apps()


def create_parser():
    """Create and configure the argument parser with tab completion."""
    parser = argparse.ArgumentParser(
        description='jtable - CLI tool for data filtering and table formatting',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    # Add the app argument and attach the completer
    app_arg = parser.add_argument(
        'app',
        help='App or filter to use (use tab completion to see available options)',
        nargs='?',
        default=None
    )

    parser.add_argument(
        '--list-apps',
        action='store_true',
        help='List all available apps and filters'
    )

    return parser


def main():
    """Main CLI entry point."""
    parser = create_parser()

    args = parser.parse_args()

    # Handle --list-apps flag
    if args.list_apps:
        print("\n".join(get_available_apps()))
        return 0

    # If app is specified, show what was selected
    if args.app:
        available = get_available_apps()
        if args.app in available:
            print(f"Selected app/filter: {args.app}")
            # Here you would normally execute the app/filter
        else:
            print(f"Error: '{args.app}' is not a valid app or filter", file=sys.stderr)
            print(f"Available options: {', '.join(available)}", file=sys.stderr)
            return 1
    else:
        # No app specified, show help
        parser.print_help()
        print(f"\nAvailable apps and filters ({len(get_available_apps())}):")
        # for app in get_available_apps():
        #     print(f"  - {app}")
        print(", ".join(get_available_apps()))

    return 0


if __name__ == "__main__":
    sys.exit(main())
