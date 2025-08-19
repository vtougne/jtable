#!/usr/bin/env python3
"""
Action-based command system for jtable.

This module implements an action-based architecture where each action
corresponds to a specific function and options map to function parameters.
Actions can be chained together with data passing between them.
"""

import json
import yaml
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
import os
import glob

# Import existing jtable components
try:
    import functions
    import to_table
    import templater
except ImportError:
    from jtable import functions
    from jtable import to_table
    from jtable import templater

class ActionContext:
    """
    Context object for passing data between actions.
    Stores named datasets and provides data access methods.
    """
    
    def __init__(self):
        self.datasets = {}
        self.vars = {}
    
    def store_dataset(self, name: str, data: Any):
        """Store a dataset with a given name."""
        self.datasets[name] = data
        logging.info(f"Stored dataset '{name}' with type {type(data).__name__}")
    
    def get_dataset(self, name: str) -> Any:
        """Retrieve a dataset by name."""
        if name not in self.datasets:
            raise ValueError(f"Dataset '{name}' not found. Available: {list(self.datasets.keys())}")
        return self.datasets[name]
    
    def list_datasets(self) -> List[str]:
        """List all available dataset names."""
        return list(self.datasets.keys())


class BaseAction(ABC):
    """
    Base class for all actions.
    Each action implements execute() method and defines its parameters.
    """
    
    def __init__(self):
        self.name = self.__class__.__name__.lower().replace('action', '')
    
    @abstractmethod
    def execute(self, context: ActionContext, **kwargs) -> Any:
        """Execute the action with given parameters."""
        pass
    
    @abstractmethod
    def get_parameters(self) -> Dict[str, Dict[str, Any]]:
        """
        Return parameter definitions for this action.
        Format: {
            'param_name': {
                'help': 'Parameter description',
                'type': str|int|bool,
                'required': True|False,
                'default': default_value
            }
        }
        """
        pass


class LoadJsonAction(BaseAction):
    """Load JSON data from file or stdin."""
    
    def get_parameters(self) -> Dict[str, Dict[str, Any]]:
        return {
            'file': {
                'help': 'Path to JSON file (or piped via stdin if not provided)',
                'type': str,
                'required': False,
                'nargs': '?'
            },
            'as': {
                'help': 'Name to store the loaded dataset as',
                'type': str,
                'required': False,
                'default': 'input',
                'dest': 'dataset_name'
            }
        }
    
    def execute(self, context: ActionContext, **kwargs) -> Any:
        file_path = kwargs.get('file')
        dataset_name = kwargs.get('dataset_name', 'input')
        
        if file_path:
            logging.info(f"Loading JSON file: {file_path}")
            with open(file_path, 'r') as f:
                data = json.load(f)
        else:
            # Check if stdin data is already in context
            if 'stdin' in context.datasets:
                stdin_data = context.get_dataset('stdin')
                if isinstance(stdin_data, str):
                    data = json.loads(stdin_data)
                else:
                    data = stdin_data
                logging.info("Loading JSON from stdin (via context)")
            else:
                # Load from stdin directly
                import sys
                stdin_content = sys.stdin.read()
                data = json.loads(stdin_content)
                logging.info("Loading JSON from stdin")
        
        context.store_dataset(dataset_name, data)
        return data


class LoadYamlAction(BaseAction):
    """Load YAML data from file or stdin."""
    
    def get_parameters(self) -> Dict[str, Dict[str, Any]]:
        return {
            'file': {
                'help': 'Path to YAML file (or piped via stdin if not provided)',
                'type': str,
                'required': False,
                'nargs': '?'
            },
            'as': {
                'help': 'Name to store the loaded dataset as',
                'type': str,
                'required': False,
                'default': 'input',
                'dest': 'dataset_name'
            }
        }
    
    def execute(self, context: ActionContext, **kwargs) -> Any:
        file_path = kwargs.get('file')
        dataset_name = kwargs.get('dataset_name', 'input')
        
        if file_path:
            logging.info(f"Loading YAML file: {file_path}")
            with open(file_path, 'r') as f:
                data = yaml.safe_load(f)
        else:
            # Check if stdin data is already in context
            if 'stdin' in context.datasets:
                stdin_data = context.get_dataset('stdin')
                if isinstance(stdin_data, str):
                    data = yaml.safe_load(stdin_data)
                else:
                    data = stdin_data
                logging.info("Loading YAML from stdin (via context)")
            else:
                # Load from stdin directly
                import sys
                stdin_content = sys.stdin.read()
                data = yaml.safe_load(stdin_content)
                logging.info("Loading YAML from stdin")
        
        context.store_dataset(dataset_name, data)
        return data


class LoadJsonFilesAction(BaseAction):
    """Load multiple JSON files using glob patterns."""
    
    def get_parameters(self) -> Dict[str, Dict[str, Any]]:
        return {
            'patterns': {
                'help': 'File patterns for JSON files (e.g., "folder/*/*.json" or "{var_name}:folder/*/*.json")',
                'type': str,
                'required': True,
                'nargs': '+'
            },
            'as': {
                'help': 'Name to store the loaded dataset as',
                'type': str,
                'required': False,
                'default': 'input_1',
                'dest': 'dataset_name'
            }
        }
    
    def execute(self, context: ActionContext, **kwargs) -> Any:
        patterns = kwargs.get('patterns', [])
        dataset_name = kwargs.get('dataset_name', 'input_1')
        
        file_list_dataset = []
        
        for pattern in patterns:
            # Handle variable name pattern like {var_name}:path
            if pattern.startswith('{') and '}:' in pattern:
                var_end = pattern.index('}:')
                dataset_name = pattern[1:var_end]
                pattern = pattern[var_end + 2:]
            
            files = glob.glob(pattern, recursive=True)
            
            for file_path in files:
                try:
                    with open(file_path, 'r') as f:
                        file_content = json.load(f)
                    
                    file_data = {
                        "name": os.path.basename(file_path),
                        "path": os.path.dirname(file_path),
                        "content": file_content
                    }
                    file_list_dataset.append(file_data)
                    
                except Exception as error:
                    logging.warning(f"Failed loading file {file_path}, skipping: {error}")
        
        context.store_dataset(dataset_name, file_list_dataset)
        return file_list_dataset


class LoadYamlFilesAction(BaseAction):
    """Load multiple YAML files using glob patterns."""
    
    def get_parameters(self) -> Dict[str, Dict[str, Any]]:
        return {
            'patterns': {
                'help': 'File patterns for YAML files (e.g., "folder/*/*.yml" or "{var_name}:folder/*/*.yml")',
                'type': str,
                'required': True,
                'nargs': '+'
            },
            'as': {
                'help': 'Name to store the loaded dataset as',
                'type': str,
                'required': False,
                'default': 'input_1',
                'dest': 'dataset_name'
            }
        }
    
    def execute(self, context: ActionContext, **kwargs) -> Any:
        patterns = kwargs.get('patterns', [])
        dataset_name = kwargs.get('dataset_name', 'input_1')
        
        file_list_dataset = []
        
        for pattern in patterns:
            # Handle variable name pattern like {var_name}:path
            if pattern.startswith('{') and '}:' in pattern:
                var_end = pattern.index('}:')
                dataset_name = pattern[1:var_end]
                pattern = pattern[var_end + 2:]
            
            files = glob.glob(pattern, recursive=True)
            
            for file_path in files:
                try:
                    with open(file_path, 'r') as f:
                        file_content = yaml.safe_load(f)
                    
                    file_data = {
                        "name": os.path.basename(file_path),
                        "path": os.path.dirname(file_path),
                        "content": file_content
                    }
                    file_list_dataset.append(file_data)
                    
                except Exception as error:
                    logging.warning(f"Failed loading file {file_path}, skipping: {error}")
        
        context.store_dataset(dataset_name, file_list_dataset)
        return file_list_dataset


class ToTableAction(BaseAction):
    """Render data as a table using the existing ToTable class."""
    
    def get_parameters(self) -> Dict[str, Dict[str, Any]]:
        return {
            'dataset': {
                'help': 'Name of dataset to render (e.g., "input", "dataset.dc_1")',
                'type': str,
                'required': False,
                'default': 'input'
            },
            'p': {
                'help': 'Path within the dataset (e.g., "hosts", "region.East[\'Data Center\'].dc_1.hosts")',
                'type': str,
                'required': False,
                'default': '{}',
                'dest': 'path'
            },
            's': {
                'help': 'Select specific columns/fields to display (comma-separated)',
                'type': str,
                'required': False,
                'default': '',
                'dest': 'select'
            },
            'us': {
                'help': 'Exclude specific columns/fields from display (comma-separated)',
                'type': str,
                'required': False,  
                'default': '',
                'dest': 'unselect'
            },
            'w': {
                'help': 'Filter rows by condition (e.g., "state == \'alive\'")',
                'type': str,
                'required': False,
                'default': '',
                'dest': 'when'
            },
            'f': {
                'help': 'Output format (simple, json, html, github, etc.)',
                'type': str,
                'required': False,
                'default': 'simple',
                'dest': 'format'
            },
            'as': {
                'help': 'Name to store the result as',
                'type': str,
                'required': False,
                'default': 'output',
                'dest': 'output_name'
            }
        }
    
    def execute(self, context: ActionContext, **kwargs) -> Any:
        dataset_name = kwargs.get('dataset', 'input')
        path = kwargs.get('path', '{}')
        select = kwargs.get('select', '')
        unselect = kwargs.get('unselect', '')
        when = kwargs.get('when', '')
        format_type = kwargs.get('format', 'simple')
        output_name = kwargs.get('output_name', 'output')
        
        # Handle nested dataset access like "dataset.dc_1"
        if '.' in dataset_name:
            parts = dataset_name.split('.')
            data = context.get_dataset(parts[0])
            for part in parts[1:]:
                if isinstance(data, dict) and part in data:
                    data = data[part]
                else:
                    raise ValueError(f"Cannot access '{part}' in dataset path '{dataset_name}'")
        else:
            data = context.get_dataset(dataset_name)
        
        # Build queryset for ToTable
        queryset = {
            'path': path,
            'format': format_type
        }
        
        if select:
            queryset['select'] = select
        if unselect:
            queryset['unselect'] = unselect  
        if when:
            queryset['when'] = when
        
        # Create ToTable instance and render
        table_renderer = to_table.ToTable()
        result = table_renderer.render_object(
            dataset=data,
            queryset=queryset,
            context=context.datasets
        )
        
        context.store_dataset(output_name, result)
        return result


class PlayAction(BaseAction):
    """Execute a query file (YAML) for advanced data transformation."""
    
    def get_parameters(self) -> Dict[str, Dict[str, Any]]:
        return {
            'query_file': {
                'help': 'Path to query file (YAML)',
                'type': str,
                'required': True
            },
            'as': {
                'help': 'Name to store the result as',
                'type': str,
                'required': False,
                'default': 'output',
                'dest': 'output_name'
            }
        }
    
    def execute(self, context: ActionContext, **kwargs) -> Any:
        query_file_path = kwargs.get('query_file')
        output_name = kwargs.get('output_name', 'output')
        
        logging.info(f"Loading query file: {query_file_path}")
        
        with open(query_file_path, 'r') as file:
            try:
                query_file = yaml.safe_load(file)
            except Exception as error:
                logging.error(f"Failed to load query file {query_file_path}: {error}")
                raise
        
        # Process the query file using existing templater logic
        # This is a simplified version - full implementation would handle vars, etc.
        if 'stdout' in query_file:
            template_str = query_file['stdout']
            
            # Create templater with to_table filter
            to_table_filter = to_table.ToTable().render_object
            template_renderer = templater.Templater(
                template_string=template_str,
                static_context=context.datasets,
                to_table_filter=to_table_filter
            )
            
            result = template_renderer.render({}, eval_str=False)
            context.store_dataset(output_name, result)
            return result
        
        return query_file


class TemplateAction(BaseAction):
    """Process a template string with optional environment variables."""
    
    def get_parameters(self) -> Dict[str, Dict[str, Any]]:
        return {
            'template': {
                'help': 'Free template string to process',
                'type': str,
                'required': True
            },
            'as': {
                'help': 'Name to store the result as',
                'type': str,
                'required': False,
                'default': 'output',
                'dest': 'output_name'
            }
        }
    
    def execute(self, context: ActionContext, **kwargs) -> Any:
        template_str = kwargs.get('template')
        output_name = kwargs.get('output_name', 'output')
        
        # Create templater
        to_table_filter = to_table.ToTable().render_object
        template_renderer = templater.Templater(
            template_string=template_str,
            static_context=context.datasets,
            to_table_filter=to_table_filter
        )
        
        result = template_renderer.render({}, eval_str=False)
        context.store_dataset(output_name, result)
        return result


# Registry of all available actions
ACTION_REGISTRY = {
    'load_json': LoadJsonAction,
    'load_yaml': LoadYamlAction, 
    'load_json_files': LoadJsonFilesAction,
    'load_yaml_files': LoadYamlFilesAction,
    'to_table': ToTableAction,
    'play': PlayAction,
    'template': TemplateAction
}


def get_action_class(action_name: str) -> BaseAction:
    """Get an action class by name."""
    if action_name not in ACTION_REGISTRY:
        available = ', '.join(ACTION_REGISTRY.keys())
        raise ValueError(f"Unknown action '{action_name}'. Available actions: {available}")
    
    return ACTION_REGISTRY[action_name]()