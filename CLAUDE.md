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