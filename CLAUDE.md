# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
Jtable is a Python CLI tool that renders tables from key/value sources like JSON, YAML, and Python dictionaries. It can be used as a CLI tool, Jinja filter (for Ansible, Django, Flask), or Python module.

## Development Commands

### Installation and Setup
The installation is not required for testing.

```bash
cd /mnt/c/data/perso/dev/project/jtable/doc/examples && cat host_list_of_dict.yml | jtable
```
It returns the following line
```
hostname    os     cost    state        env
----------  -----  ------  -----------  -----
host_1      linux  5000    alive        qua
host_2      linux  5000    alive        qua
host_3      linux          unreachable  qua
```

## CLI Commands and Options

### Load Commands
- `load_json <file>` : Load a single JSON file (or from stdin if no file provided)
- `load_yaml <file>` : Load a single YAML file (or from stdin if no file provided)
- `load_json_files <patterns...>` : Load multiple JSON files using glob patterns
- `load_yaml_files <patterns...>` : Load multiple YAML files using glob patterns
- `play <query_file>` : Execute a query file for advanced data transformation

### Options
- `-p, --json_path` : Specify a path in the input data (e.g., `hosts`, `region.East['Data Center'].dc_1.hosts`)
- `-s, --select` : Select specific columns/fields to display
- `-us, --unselect` : Exclude specific columns/fields from display
- `-w, --when` : Filter rows by condition (e.g., `state == 'alive'`)
- `-f, --format` : Output format (simple, json, th, td, html, github, latex, etc.)
- `-q, --query_file` : Load a query file (YAML) for complex transformations
- `--inspect` : Inspect and display all paths/values in the input data
- `-vq, --view_query` : Show the generated query structure
- `-o, --stdout` : Override output filter
- `-pf, --post_filter` : Apply an additional filter to the output
- `--version` : Show version information
- `-v, --verbose` : Increase verbosity level
- `-d, --debug` : Enable debug mode
- `-h, --help` : Show help message

### Testing
```bash
# All available commands / options are described in doc/examples/doc_script.yml
# it is encapsulated bu doc/examples/make_doc.sh
# make_doc.sh:
# ../../make_doc.py -i doc_script.yml -o README.md $@

# Run the full test suite
cd /mnt/c/data/perso/dev/project/jtable/doc/examples && ./make_doc.sh --halt

# Check if a difference is found
cd /mnt/c/data/perso/dev/project/jtable/doc/examples && ./diff_doc.sh ref_README.md README.md '^[0-2][0-9]:[0-6][0-9]:[0-6][0-9]'

# If ok the result should be:
cmd: diff --side-by-side --suppress-common-lines ref_README.md README.md | egrep -v "^[0-2][0-9]:[0-6][0-9]:[0-6][0-9]"
Success No differences found
```

### Test Validation
The test suite compares generated output against reference files using `diff_doc.sh`. Tests fail if output differs from expected results (excluding timestamps). The `make_doc.sh --halt` script generates documentation examples that must match the reference output in `ref_README.md`.

## Architecture

### Core Components
- **jtable/jtable.py**: Main CLI entry point and JtableCli class
- **jtable/to_table.py**: ToTable class for rendering data to tables
- **jtable/templater.py**: Templater class for Jinja template processing
- **jtable/functions.py**: Plugin system and utility functions
- **jtable/logger.py**: Custom logging configuration

### Key Classes
- `JtableCli`: Main CLI handler
- `ToTable`: Core table rendering engine
- `Templater`: Jinja template processor with jtable filters
- `Plugin`: Utility functions for templates (env vars, data manipulation)

### Data Flow
1. Input sources (JSON/YAML/stdin) → 
2. Data parsing and loading → 
3. Query/template processing (optional) → 
4. Table rendering with ToTable → 
5. Output formatting (plain/HTML/JSON/etc.)

### Template System
- Uses Jinja2 with custom filters
- Query files allow complex data transformation
- Supports conditional coloring and formatting
- Template files use `.j2` extension

### Directory Structure
- `jtable/`: Main package code
- `doc/examples/`: Usage examples and sample queries
- `testings/`: Test files and sample data => this part only for user testing, do not use this folder as context

### Key Features Implementation
- Multi-format output via tabulate library
- Ansible integration through Jinja filters
- Data inspection via InspectDataset class
- Path auto-discovery for nested data structures

## Usage Examples

### Basic Table Rendering
```bash
# Display list of dictionaries as table
cd /mnt/c/data/perso/dev/project/jtable/doc/examples && cat host_list_of_dict.yml | jtable

# Load single files
cd /mnt/c/data/perso/dev/project/jtable/doc/examples && jtable load_yaml host_list_of_dict.yml
cd /mnt/c/data/perso/dev/project/jtable/doc/examples && jtable load_json host_list_of_dict.json

# Access nested data with path
cd /mnt/c/data/perso/dev/project/jtable/doc/examples && cat host_list_of_dict_in_key.yml | jtable -p hosts
cd /mnt/c/data/perso/dev/project/jtable/doc/examples && cat key_containing_space.yml | jtable -p "region.East['Data Center'].dc_1.hosts"
```

### Query File Features
- **Data Transformation**: Convert data types, calculate values (e.g., seconds to days)
- **Conditional Formatting**: Apply colors and styling based on data values
- **Variable Mapping**: Create lookup tables and views for data enrichment
- **Multi-file Aggregation**: Combine data from multiple sources with context
- **Jinja Templating**: Use full Jinja2 syntax for complex data manipulation

### Ansible Integration
```yaml
# In Ansible playbooks
- debug:
    msg: "{{ host_list | jtable }}"
```


# Todo

## New endpoints
```
CLI Endpoints:
- jtable            # old CLI kept until the CLI below will replace it
- jtable-filter     # Filter cascading
- jtable-play       # Play a sequence written in yaml
- jtable-template   # Template string or file
```

### jtable-filter


```
jtable-filter usage:
    # first action may be a module, for example load_json, and the suite is anytime a filter
      jtable-filter [module <module options>] [ filter <filer options> ] [ filter <filter options> ]

    # Or a filter, assuming data are piped from stdin
      echo <some_data> | jtable-filter [ filter <filer options> ] [ filter <filter options> ]
    

    # Examples
        jtable-filter load_json <json_file> to_table -p hosts -s hostname,os,state
        # will be equivalent to 
        jtable-filter load_json <json_file> to_nice_yaml
        cat hosts_dataset.json | jtable-filter from_json to_table -p hosts -s hostname,os,state
```

### jtable-play

```
jtable-play:
    jtable [-f|--file] <jtable_playbook.yml> 
    jtable <jtable_playbook.yml> -v "first_name=john" -d '{"last_name": "Doe"}'
```


### jtable-template
```
jtable-template:
    echo John | jtable-template "Hello {{ stdin }}"
```

## tasks:

```
1- jtable-play (CLI):
    Parse user inputs and option, and call player module
    options
    -v   | --var      # Add a variable in format key=value (can be used multiple times)
    -d   | --dict     # Add variables from JSON dictionary (can be used multiple times)
    -E   | --env      # Expose OS env vars directly ({{ PATH }}, {{ HOME }})
    -En  | --env-ns   # Store OS env vars in namespace (usage: -En my_var creates {{ my_var }} containing env())


2- player (Class):
    The Player class (jtable/player.py) executes jtable playbooks (YAML query files).
    It provides the core engine for the jtable-play CLI command.

    Key Responsibilities:
    - Load and parse YAML playbook files
    - Manage execution context with variables and datasets
    - Process vars section from playbook with Jinja template evaluation
    - Execute playbook stdout expression using Templater
    - Support stdin data injection into templates

    Main Methods:
    - __init__(playbook_file, variables=None, stdin_data=None)
      Initialize Player with playbook path, optional variables dict, and stdin data
      Variables are injected into the execution context for template rendering

    - load_playbook()
      Load and parse YAML playbook file
      Validates file existence and YAML format
      Exits with error code 2 if loading fails

    - prepare_context()
      Prepare execution context by:
      1. Starting with command-line provided variables
      2. Processing 'vars' section from playbook (Jinja template evaluation)
      3. Merging all variables into dataset for template rendering
      4. Making variables available as {{ vars.key }} and {{ key }}

    - execute() -> str
      Execute the playbook and return rendered output:
      1. Load playbook
      2. Prepare context
      3. Handle queryset if present in vars
      4. Render stdout expression using Templater
      Returns: Rendered output string

    Usage Flow:
    1. jtable-play CLI parses command-line arguments
    2. Creates Player instance with playbook file and variables
    3. Calls player.execute() to get output
    4. Prints output to stdout

    Template Context:
    - Command-line variables: Available as {{ var_name }}
    - Playbook vars: Available as {{ vars.var_name }}
    - Stdin data: Available as {{ stdin }}
    - Environment vars (if -E): Available as {{ PATH }}, {{ HOME }}, etc.
    - Environment vars (if -En ns): Available as {{ ns.PATH }}, {{ ns.HOME }}, etc.
    - Queryset: Available as {{ queryset }}

    Implementation Details:
    - Uses create_templater() helper to create Templater instances with to_table filter
    - Supports eval_str=True for vars evaluation (converts string representations)
    - Supports eval_str=False for stdout rendering (preserves formatting)
    - Integrates with ToTable for table rendering via jtable filter

2- jtable-template:
    build a in_memory playbook and give it to  Player classe
    it will have the same behavior with jtable template
    jtable-template -E "Hello {{ LOGNAME }}, how are you ?"
    will return Hello vince, how are you ?
    like old method, jtable template -E "Hello {{ LOGNAME }}, how are you ?"

    options:
    -E   | --env        # Expose OS env vars directly
    -En  | --env-ns     # Store OS env vars in namespace
    -vp  | --view-play  # Display the playbook in yaml format without executing it


```
