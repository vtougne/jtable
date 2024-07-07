#!/usr/bin/env python3
import argparse

def start_command(args):
    print(f"Starting process from group: {args.from_group}")

def main():
    parser = argparse.ArgumentParser(description='My Script Description')

    subparsers = parser.add_subparsers(dest='command', help='Sub-command help')

    # Parser for the "start" command
    start_parser = subparsers.add_parser('start', help='Start command help')
    start_parser.add_argument('--from_group', required=True, help='Group to start from')

    # Parse the arguments
    args = parser.parse_args()

    # Execute the appropriate function based on the command
    if args.command == 'start':
        start_command(args)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
