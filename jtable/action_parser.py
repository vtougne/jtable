#!/usr/bin/env python3
"""
Action-based argument parser for jtable.

This module implements argument parsing that can handle action chaining
where multiple actions can be executed in sequence with data passing
between them.
"""

import argparse
import sys
import logging
from typing import List, Dict, Any, Tuple
try:
    from actions import ACTION_REGISTRY, get_action_class, ActionContext
except ImportError:
    from jtable.actions import ACTION_REGISTRY, get_action_class, ActionContext


class ActionChainParser:
    """
    Parser that can handle chained actions with their respective options.
    
    Example usage:
    jtable load_json file.json --as dataset to_table -p dataset.dc_1 -s hostname,ip,state
    """
    
    def __init__(self):
        self.context = ActionContext()
    
    def parse_action_chain(self, args: List[str]) -> List[Dict[str, Any]]:
        """
        Parse a list of arguments into a chain of actions with their parameters.
        
        Args:
            args: Command line arguments
            
        Returns:
            List of dictionaries, each containing action name and parsed arguments
        """
        if not args:
            return []
        
        action_chains = []
        current_action = None
        current_args = []
        
        i = 0
        while i < len(args):
            arg = args[i]
            
            # Check if this argument is an action name
            if arg in ACTION_REGISTRY:
                # If we have a previous action, process it
                if current_action:
                    action_chains.append(self._parse_single_action(current_action, current_args))
                
                # Start new action
                current_action = arg
                current_args = []
            else:
                # Add argument to current action
                if current_action is None:
                    raise ValueError(f"No action specified before argument '{arg}'")
                current_args.append(arg)
            
            i += 1
        
        # Process the last action
        if current_action:
            action_chains.append(self._parse_single_action(current_action, current_args))
        
        return action_chains
    
    def _parse_single_action(self, action_name: str, args: List[str]) -> Dict[str, Any]:
        """
        Parse arguments for a single action.
        
        Args:
            action_name: Name of the action
            args: Arguments for this action
            
        Returns:
            Dictionary with action name and parsed arguments
        """
        action_class = get_action_class(action_name)
        parameters = action_class.get_parameters()
        
        # Create argument parser for this action
        parser = argparse.ArgumentParser(add_help=False, prog=f'jtable {action_name}')
        
        # Add parameters to parser
        for param_name, param_config in parameters.items():
            parser_kwargs = {}
            
            # Handle special parameter configurations
            if 'dest' in param_config:
                parser_kwargs['dest'] = param_config['dest']
            
            if param_config.get('required', False):
                parser_kwargs['required'] = True
            
            if 'default' in param_config:
                parser_kwargs['default'] = param_config['default']
            
            if 'nargs' in param_config:
                parser_kwargs['nargs'] = param_config['nargs']
            
            if 'help' in param_config:
                parser_kwargs['help'] = param_config['help']
            
            if param_config.get('type'):
                parser_kwargs['type'] = param_config['type']
            
            # Handle positional vs optional arguments
            if param_name in ['file', 'query_file', 'template', 'patterns']:
                # These are positional arguments
                parser.add_argument(param_name, **parser_kwargs)
            else:
                # These are optional arguments with flags
                if len(param_name) == 1:
                    parser_args = [f'-{param_name}']
                else:
                    parser_args = [f'--{param_name}']
                parser.add_argument(*parser_args, **parser_kwargs)
        
        # Parse the arguments
        try:
            parsed_args = parser.parse_args(args)
            return {
                'action': action_name,
                'args': vars(parsed_args)
            }
        except SystemExit as e:
            # argparse calls sys.exit on error, catch it and re-raise as exception
            raise ValueError(f"Failed to parse arguments for action '{action_name}': {args}")
    
    def execute_action_chain(self, action_chains: List[Dict[str, Any]]) -> Any:
        """
        Execute a chain of actions in sequence.
        
        Args:
            action_chains: List of action dictionaries from parse_action_chain
            
        Returns:
            Result from the last action
        """
        last_result = None
        
        for action_chain in action_chains:
            action_name = action_chain['action']
            args = action_chain['args']
            
            logging.info(f"Executing action '{action_name}' with args: {args}")
            
            action_instance = get_action_class(action_name)
            
            try:
                result = action_instance.execute(self.context, **args)
                last_result = result
                logging.info(f"Action '{action_name}' completed successfully")
            except Exception as error:
                logging.error(f"Action '{action_name}' failed: {error}")
                raise
        
        return last_result
    
    def parse_and_execute(self, args: List[str]) -> Any:
        """
        Parse arguments and execute the action chain.
        
        Args:
            args: Command line arguments
            
        Returns:
            Result from the last action
        """
        action_chains = self.parse_action_chain(args)
        if not action_chains:
            raise ValueError("No actions specified")
        
        return self.execute_action_chain(action_chains)


def create_legacy_compatible_parser() -> argparse.ArgumentParser:
    """
    Create a legacy-compatible argument parser that supports both
    old-style subcommands and new action chaining.
    """
    parser = argparse.ArgumentParser(
        prog='jtable',
        description='Tabulate your JSON/Yaml data and transform it using Jinja',
        add_help=True
    )
    
    # Add version
    parser.add_argument('--version', action='version', version='1.0.0')  # TODO: Import from version
    
    # Add global options that apply to all actions
    parser.add_argument('-v', '--verbose', action='count', default=0, help='Verbosity level')
    parser.add_argument('-d', '--debug', action='store_true', help='Add code row number in log')
    
    return parser


def detect_parsing_mode(args: List[str]) -> str:
    """
    Detect whether we should use legacy parsing or new action chaining.
    
    Args:
        args: Command line arguments
        
    Returns:
        'legacy' or 'action_chain'
    """
    if not args:
        return 'legacy'
    
    # Count how many action names we have
    action_count = sum(1 for arg in args if arg in ACTION_REGISTRY)
    
    if action_count > 1:
        return 'action_chain'
    elif action_count == 1:
        # Check if we have --as flag, which indicates action chaining intent
        if '--as' in args:
            return 'action_chain'
        # Check if we have multiple action words that could be chained
        for i, arg in enumerate(args):
            if arg in ACTION_REGISTRY and i + 1 < len(args):
                # Look ahead for potential second action
                remaining_args = args[i+1:]
                if any(a in ACTION_REGISTRY for a in remaining_args):
                    return 'action_chain'
    
    return 'legacy'


def stdin_has_data() -> bool:
    """Check if there's data available on stdin."""
    return not sys.stdin.isatty()


def handle_stdin_data() -> str:
    """Read data from stdin."""
    data = ""
    for line in sys.stdin:
        data += line
    return data


if __name__ == "__main__":
    # Test the action chain parser
    test_args = ['load_json', 'test.json', '--as', 'dataset', 'to_table', '-p', 'dataset.dc_1', '-s', 'hostname,ip']
    
    parser = ActionChainParser()
    chains = parser.parse_action_chain(test_args)
    
    print("Parsed action chains:")
    for chain in chains:
        print(f"  {chain}")