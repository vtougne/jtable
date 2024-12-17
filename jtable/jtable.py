#!/usr/bin/env python3
import sys, json, re, os, ast, inspect, datetime, time, logging, logging.config, html, shutil, platform
from os import isatty
from sys import exit
from typing import Any, Dict, Optional
# import filters as Filters

jtable_path = os.path.dirname(os.path.abspath(__file__))

if jtable_path not in sys.path:
    sys.path.insert(0, jtable_path)
from logger import CustomFormatter, CustomFilter, _ExcludeErrorsFilter, logging_config

import version
import tabulate
import yaml

running_platform = platform.system()

def ms_system():
    return os.environ.get('MSYSTEM', '')

if running_platform == "Windows":
    if ms_system == "MINGW64" or ms_system == "CLANGARM64":
        running_os = "Linux"
    elif os.environ.get('TERM', '')  == "xterm":
            running_os = "Linux"
    else:
        running_os = "Windows"
else:
    running_os = running_platform


class Filters:
    def b64decode(value):
        import base64
        return base64.b64decode(value).decode('utf-8')
    def b64encode(value):
        import base64
        return base64.b64encode(value.encode('utf-8')).decode('utf-8')
    def escape(value,format="html"):
        if format == "html":
            return html.escape(value)
        elif format == "quote":
            return value.replace('\\', '\\\\').replace('"', '\\"')
    def unescape(value,format="html"):
        if format == "html":
            return html.unescape(value)
        elif format == "quote":
            return value.replace('\\"', '"').replace('\\\\', '\\')

    def flatten(matrix):
        return [item for row in matrix for item in row]
    def from_json(str):
        return json.loads(str)
    def from_yaml(data):
        return yaml.safe_load(data)
    def from_json_or_yaml(data):
        return yaml.safe_load(data)
    def from_yaml_all(data):
        return yaml.safe_load_all(data)
    def intersect(a, b):
        return list(set(a).intersection(b))
    def wrap_html(data,title=""):
        if running_platform == "Windows":
            path_sep = "\\"
        else:
            path_sep = "/"
        base_path = getattr(sys, '_MEIPASS', os.path.abspath(path_sep.join(__file__.split(path_sep)[:-1])))
        logging.info(f"base_path: {base_path}")
        resources_path = f"{base_path}{path_sep}resources"
        def load_file(expected_file_name):
            with open(resources_path + path_sep + expected_file_name, 'r') as file:
                content = file.read()
            return content
        
        js_wrapper_css = load_file("js_wrapper.css")
        js_wrapper_script = load_file("js_wrapper.js")

        return f"""<!DOCTYPE html>
<html lang="fr">
<html>
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.6.4/jquery.min.js"></script>
        <style>
          {js_wrapper_css}
        </style>
    <body>
    <div id="toc"></div>
    {data}
    <button id="scrollTopButton" onclick="scrollToTop()">Top</button>
    <script>
      {js_wrapper_script}
    </script>
    </body>
</html>
          """
    def jtable(dataset,select=[], unselect=[],path="{}",format="",views={}, when=[],context = {}, queryset={}):
        return JtableCls().render_object( dataset,path=path, select=select, unselect=unselect,views=views, when=when, format=format, context = context, queryset=queryset)
    def m5(data):
        import hashlib
        return hashlib.md5(data.encode()).hexdigest()
    def regex_replace(value="", pattern="", replacement="", ignorecase=False):
        """ Perform a `re.sub` returning a string """
        if ignorecase:
            flags = re.I
        else:
            flags = 0
        _re = re.compile(pattern, flags=flags)
        return _re.sub(replacement, value)
    def strftime(string_format, second=None):
        """ return a date string using string.
        See https://docs.python.org/2/library/time.html#time.strftime for format
        timestamp option strftime(s) Doesn't works on Cygwin => old known cygwin issue """

        if second is not None:
            try:
                second = int(second)
            except Exception:
                raise "Invalid value for epoch value (%s)" % second
        return time.strftime(string_format, time.localtime(second))
    def to_datetime(_string, format=r"%Y-%m-%d %H:%M:%S"):
            return datetime.datetime.strptime(_string, format)
    def to_epoch(date_str):
        f"""Convert a date string to epoch
        Args:
            date_str (str): Date string format: %Y-%m-%d %H:%M:%S !!! only !!!
        """
        if running_platform == "Windows":
            return int(Plugin.shell(f"powershell -c \"[math]::Round((Get-Date '{date_str}' -UFormat '%s'))\""))
        else:
            return int(time.mktime(datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S").timetuple()))
    def to_json(a, *args, **kw):
        return json.dumps(a, *args, **kw)
    def to_pie(dataset):
        title = [list(key.keys()) for key in dataset][0][0]
        out = f"```mermaid\n  pie\n      title {title}\n"
        for item in dataset:
            item_prop = list(item.keys())
            # logging.warning(f"item_prop: {item[item_prop[0]]}")
            out = out + f"      \"{item[item_prop[0]]} ({str(item[item_prop[1]])})\" : {str(item[item_prop[1]])}\n"
        out = out + "```"
        return out
    def to_nice_json(v, *args, **kw):
        out = json.dumps(v, indent=2, separators=(',', ': '))
        return out    
    def to_nice_yaml(v,indent=2):
        return yaml.dump(v, allow_unicode=True,indent=indent)
    def to_yaml(v):
        out = "".join([v.strip() for v in yaml.dump(v,default_flow_style=True).split('\n')])
        return out
    def type_debug(o):
        return  o.__class__.__name__

class Inspect:
    def __init__(self):
        self.out = []
    def add_row(self,row):
        self.out = self.out + [ [row[0]] + [row[1]] ]
        logging.info("Covering " + " / ".join(Filters.flatten([ [row[0]] + [row[1]] ])))
    def view_paths(self,dataset,path="", max_depth=0):
        self.cover_data(dataset,path="", max_depth=0)
        return self.out
    def cover_data(self,dataset,path="", max_depth=0):
        if type(dataset) is dict:
            for key,value in dataset.items():
                if " " in str(key):
                    the_path = path + "['" + str(key) + "']"
                else:
                    if path == "":
                        the_path = path + str(key)
                    else:
                        the_path = path + "." + str(key)
                self.cover_data(value,the_path )
        elif type(dataset) is list:
            index=0
            for item in dataset:
                the_path = path + "[" + str(index) + "]"
                # logging.warning(f"the_path: {the_path}")
                index += 1
                self.cover_data(item,the_path)
        else:
            self.add_row([path] + [str(dataset)])

class JtableCli:
    def __init__(self):
        self.path = ""
        self.dataset = {}
        
        global BaseLoader,Environment
        from jinja2 import Environment, BaseLoader

        
    def parse_args(self):

        select = []
        queryset = {}
        self.tabulate_var_name="stdin"
        if 'JTABLE_RENDER' in os.environ:
            render=os.environ['JTABLE_RENDER']
        else:
            render="jinja_native"

        import argparse

        parser = argparse.ArgumentParser(description='Tabulate your JSON/Yaml data and transform it using Jinja',add_help=False)

        parser.add_argument("-h", "--help",nargs="*", help = "Show this help")
        parser.add_argument("-p", "--json_path", help = "json path")
        parser.add_argument("-s", "--select", help = "select key_1,key_2,...")
        parser.add_argument("-w", "--when", help = "key_1 == 'value'")
        parser.add_argument("-f", "--format", help = "Table format applied in simple,json,th,td... list below")
        parser.add_argument("-us", "--unselect", help = "Unselect unwanted key_1,key_2,...")
        parser.add_argument("-q", "--query_file", help = "Load jtbale query file")
        parser.add_argument("--inspect", action="store_true", help="Inspect stdin")
        parser.add_argument("-jf", "--json_file", help = "Load json")
        parser.add_argument("-jfs", "--json_files", action='append', help = "Load multiple Json's")
        parser.add_argument("-yfs", "--yaml_files", action='append', help = "Load multiple Yaml's")
        parser.add_argument("-vq", "--view_query", action="store_true", help = "View query")
        parser.add_argument('--version', action='version', version=version.__version__)
        parser.add_argument('-v', '--verbose', action='count', default=0, help='Verbosity level')
        parser.add_argument('-d', '--debug', action="store_true", help='Add code row number in log')
        parser.add_argument('-o', '--stdout', help='Ovewrite applied ouput filter, default: {{ stdin | jtable(queryset=queryset) }}')
        parser.add_argument('-pf', '--post_filter', help='Additionnal filter to apply on stdout, eg: jtable ..-f json -pf "from_json | to_nice_yaml"')

        args = parser.parse_args()
        global terminal_size
        terminal_size = shutil.get_terminal_size((80, 20))  # Largeur par défaut 80, hauteur 20
        # logging.warning(f"terminal_size: {terminal_size}")  

        if os.environ.get('JTABLE_LOGGING') == "DEBUG" or args.debug:
            logging_config['formatters']['my_formatter']['format'] = '%(asctime)s (%(lineno)s) %(class_name)s.%(parent_function)-16s | %(levelname)s %(message)s'
        else:
            logging_config['formatters']['my_formatter']['format'] = '%(asctime)s %(class_name)s.%(parent_function)-15s | %(levelname)s %(message)s'

        
        if args.verbose == 0:
            logging_config['handlers']['console_stderr']['level'] = 'WARNING'
        if args.verbose == 1:
            logging_config['handlers']['console_stderr']['level'] = 'INFO'
        elif args.verbose == 2:
            logging_config['handlers']['console_stderr']['level'] = 'DEBUG'
        logging.config.dictConfig(logging_config)
        logging.info(f"running_os: {running_os}")
        
        # global logging_format
        # logging_format = '%(asctime)s (%(lineno)s) %(class_name)s.%(parent_function)s | %(levelname)s %(message)s'
        
        if args.query_file:
            logging.info(f"loading query file: {args.query_file}")
            with open(args.query_file, 'r') as file:
                try:
                    query_file = yaml.safe_load(file)
                except Exception as error:
                    logging.error(f"Fail to load query file {args.query_file}, check Yaml format")
                    logging.error(f"error was:\n{error}")
                    exit(2)
                
            if 'vars' in query_file:
                if 'queryset' in query_file['vars']:
                    queryset = query_file['vars']['queryset']
            if 'secrets' in query_file:
                global secrets
                secrets = query_file['secrets']

                
        is_pipe = not isatty(sys.stdin.fileno())

        stdin=""
        if is_pipe:
            logging.info("stdin is a pipe")
            for line in sys.stdin:
                stdin = stdin + line
            self.dataset = { self.tabulate_var_name: stdin }

        if args.help:
            if args.help == ['color']:
                jtable_color = [name for name, func in inspect.getmembers(Styling().__init__())]
                print(Styling().view_all_colors())
                exit(1)
            else:
                print(f"Error: No help available for '{args.help[0]}'")
                exit(1)


        if not is_pipe and not args.json_file and not args.json_files and not args.query_file and not args.yaml_files and not args.stdout:

            parser.print_help(sys.stdout)
            jtable_core_filters = [name for name, func in inspect.getmembers(Filters, predicate=inspect.isfunction)]
            jtable_plugins = [name for name, func in inspect.getmembers(Plugin, predicate=inspect.isfunction)]
            print(f"\njtable core filters:\n   {', '.join(jtable_core_filters)}\n")
            tablulate_formats = next((value for name, value in inspect.getmembers(tabulate) if name == 'tabulate_formats'), None)
            jtable_formats = ['json','th','td']
            print(f"tabulate formats:\n   {', '.join(sorted(tablulate_formats))}\n")
            print(f"jtable additional formats:\n   {', '.join(sorted(jtable_formats))}\n")
            print(f"jtable plugins:\n   {', '.join(jtable_plugins)}\n")
            print(f"More help with jtable -h <help topic>")
            print(f"  colors:\n    type jtable -h color | jtable\n")
            exit(1)

        if args.json_file:
            logging.info(f"loading json file: {args.json_file}")
            got_variable_name_pattern = r'^\{[a-zA-Z_1-9]+\}:.*'
            if re.match(got_variable_name_pattern, args.json_file):
                self.tabulate_var_name = args.json_file[1:].split('}:')[0]
                file_name = ':'.join(args.json_file.split(':')[1:])
            else:
                self.tabulate_var_name = "input_1"
                file_name = args.json_file
            logging.info(f"file_name: {file_name}, self.tabulate_var_name: {self.tabulate_var_name}")
            with open(file_name, 'r') as input_yaml:
                self.dataset = {**self.dataset, **{ self.tabulate_var_name: yaml.safe_load(input_yaml) } }
                
        def load_multiple_inputs(file_search_string,format):
            logging.info(f"loading {format} files: {file_search_string}")
            err_help = f"\n[ERROR] {format}_files must looks like this:\n\n\
                jtable --{format}_files \"{{target_var_name}}:folder_1/*/*/config.yml\"\n"
            got_variable_name_pattern = r'^\{[a-zA-Z_1-9]+\}:.*'
            if re.match(got_variable_name_pattern, file_search_string):
                logging.info(f"Contains variable name file_names: {file_search_string}")
                splitted_path = file_search_string[1:].split('}:')
                path=splitted_path[1]
                self.tabulate_var_name = splitted_path[0]
            else:
                self.tabulate_var_name = "input_1"
                logging.info(f"Adding var_name: {self.tabulate_var_name}")
                path = file_search_string
            logging.info(f"var_name: {self.tabulate_var_name}, path: {path}")
            logging.info(f"path: {path}")
            
            if running_os == "Windows":
                cmd = f"dir /s /b {path}"
                logging.info(f"cmd: {cmd}")
                files_str = os.popen("dir /s /b " + path).read()
            else:
                files_str = os.popen("ls -1 " + path).read()
            # for windows syntax will be --> # dir /s /b data\*config.yml
            file_list_dataset = []
            for file_name_full_path in files_str.split('\n'):
                if file_name_full_path != '':
                    with open(file_name_full_path, 'r') as input_yaml:
                        try:
                            file_content =  yaml.safe_load(input_yaml)
                            if running_os == "Windows":
                                sep = "\\"
                                file_path = sep.join(file_name_full_path.split('\\')[:-1])
                                file_name = file_name_full_path.split('\\')[-1]
                            else:
                                file_path = "/".join(file_name_full_path.split('/')[:-1])
                                file_name = file_name_full_path.split('/')[-1]
                            file = { 
                                    "name": file_name,
                                    "path": file_path,
                                    "content": file_content
                                    }
                            file_list_dataset = file_list_dataset + [{ **file }]
                        except Exception as error:
                            logging.warning(f"fail loading file {file_name_full_path}, skipping")
            self.dataset = {**self.dataset, **{ self.tabulate_var_name: file_list_dataset } }
        
        if args.json_files:
            for file in args.json_files:
                load_multiple_inputs(file,"json")

        if args.yaml_files:
            for file in args.yaml_files:
                load_multiple_inputs(file,"yaml")
        
        if args.json_path:
            new_path = args.json_path
            expr_end_by_braces=(re.sub('.*({).*(})$',r'\1\2',args.json_path))
            if expr_end_by_braces != "{}":
                new_path = new_path + "{}"
            queryset['path'] = new_path

        if args.query_file:
            if 'sources' in query_file:
                for source_name in query_file['sources']: 
                    if 'json_files' in query_file['sources'][source_name]:
                        expr = query_file['sources'][source_name]['json_files']
                        expr_with_name = f"{{{source_name}}}:{expr}"
                        load_multiple_inputs(expr_with_name,"json")
                    if 'yaml_files' in query_file['sources'][source_name]:
                        expr = query_file['sources'][source_name]['yaml_files']
                        expr_with_name = f"{{{source_name}}}:{expr}"
                        load_multiple_inputs(expr_with_name,"yaml")
                    if 'shell' in query_file['sources'][source_name]:
                        shell_command = query_file['sources'][source_name]['shell']
                        jinja_eval = Templater(template_string=str(shell_command), static_context=self.dataset).render({},eval_str=True)
                        logging.info(f"Launch shell, cmd: {jinja_eval}")
                        shell_output = Plugin.shell(jinja_eval)
                        self.dataset = {**self.dataset, **{ source_name: shell_output } }

                    if 'env' in query_file['sources'][source_name]:
                        env_var = query_file['sources'][source_name]['env']
                        env_value = Plugin.env(env_var)
                        self.dataset = {**self.dataset, **{ source_name: env_value } }
            if 'vars' in query_file:
                vars = {}
                for key,value in query_file['vars'].items():
                    logging.info(f"Covering vars, key: {key}")
                    jinja_eval = Templater(template_string=str(value), static_context=self.dataset).render({},eval_str=True)
                    vars.update({key: jinja_eval})
                    self.dataset = {**self.dataset,**vars, **{"vars": vars}}

            
        if 'select' in queryset:
            select = queryset['select']

        if args.unselect:
           queryset['unselect'] = args.unselect

        if args.select:
            queryset['select'] = args.select

        if args.when:
            queryset['when'] = args.when

        if not 'path' in queryset:
            queryset['path'] = "{}"
                    
        if not "format" in queryset:
            queryset['format'] = 'simple'

        if args.format:
            queryset['format'] = args.format

        if args.view_query:
            original_format = queryset['format']
            queryset['format'] = "th"
            
        if args.stdout:
            out_expr = args.stdout
        else:
            if self.tabulate_var_name == "stdin":
                if args.post_filter:
                    original_out_expr = "{{ " + self.tabulate_var_name + " | from_json_or_yaml | jtable(queryset=queryset) }}"
                    out_expr = "{{ " + self.tabulate_var_name + f" | from_json_or_yaml | jtable(queryset=queryset) | {args.post_filter} }}}}"
                else:
                    out_expr = "{{ " + self.tabulate_var_name + " | from_json_or_yaml | jtable(queryset=queryset) }}"
            else:
                out_expr = "{{ " + self.tabulate_var_name + " | jtable(queryset=queryset) }}"


        if args.query_file:
            if 'stdout' in query_file:
                out_expr = query_file['stdout']
            
        if args.inspect:
            if self.tabulate_var_name == "stdin":
                inspected_paths = Inspect().view_paths(yaml.safe_load(stdin))
            else:
                inspected_paths = Inspect().view_paths(self.dataset[self.tabulate_var_name])
            tbl = tabulate.tabulate(inspected_paths,['path','value'])
            print(tbl)
            return

        if args.view_query:
            if args.post_filter:
                out = Templater(template_string=original_out_expr, static_context={**self.dataset,**{"queryset": queryset}}).render({},eval_str=True)
            else:
                out = Templater(template_string=out_expr, static_context={**self.dataset,**{"queryset": queryset}}).render({},eval_str=True)
            query_file_out = {}
            query_set_out = {}
            fields = out
            if select == []:
                for field in fields:
                    select = select + [ {'as': field, 'expr': field }  ]
            query_set_out['path'] = queryset['path']
            query_set_out['select'] = select
            query_set_out['format'] = original_format
            if args.when:
                query_set_out['when'] = args.when
            query_file_out['vars'] = {'queryset': query_set_out }
            # if args.post_filter:
            #     query_file_out['vars'].update({'prepa_stdout': f"{out_expr}" })
            # query_file_out['stdout'] = f"{{{{ prepa_stdout | {args.post_filter} }}}}"
            query_file_out['stdout'] = out_expr



            yaml_query_out = yaml.dump(query_file_out, allow_unicode=True,sort_keys=False)
            print(yaml_query_out)
        else:
            logging.info(f"queryset: {queryset}")
            out = Templater(template_string=out_expr, static_context={**self.dataset,**{"queryset": queryset}}).render({},eval_str=False)
            print(out)

class JtableCls:
    def __init__(self, render="jinja_native"):
        logging.info(f"Initilizing render: {render}")
        self.td = []
        self.th = []
        self.table_headers = []
        self.json = []
        self.render = render
        self.splitted_path = []
        self.when = []
        self.select = []
        self.unselect = []
        self.views = {}
        self.path = "{}"
        self.format = ""

        if self.render == "jinja_ansible":
            global Templar,AnsibleContext,AnsibleEnvironment
            from ansible.template import Templar,AnsibleContext,AnsibleEnvironment
            from ansible.parsing.dataloader import DataLoader
            self.loader = DataLoader()
        elif self.render == "jinja_native":
            self.loader=BaseLoader()
            self.tenv = Environment(loader=self.loader)
            jtable_core_filters = [name for name, func in inspect.getmembers(Filters, predicate=inspect.isfunction)]
            for filter_name in jtable_core_filters:
                self.tenv.filters[filter_name] = getattr(Filters, filter_name)
        elif self.render == "jinja_ansible_extensions":
            self.tenv = Environment(extensions=['jinja2_ansible_filters.AnsibleCoreFiltersExtension'])
        else:
            logging.error("Unknown render option")
            exit(1)
    
    def cross_path(self, dataset, path, cross_path_context = {} ):
        level = len(path)
        if level > 1:
            # logging.info(f"path: {path}")
            next_path = path[1:]
            current_path = str(path[0])
            current_path_value = "unknown"
            if current_path[0:2] == "['":
                current_path_value = current_path[2:-2]
                if current_path_value in list(dataset):
                    self.cross_path(dataset[current_path_value], next_path, cross_path_context = cross_path_context)
                    # try:
                    #     self.cross_path(dataset[current_path_value], next_path, cross_path_context = cross_path_context)
                    # except:
                    #     logging.error(f"Failed while crossing path: {current_path_value}")
                    #     exit(1)
                else:
                    logging.error('keys dataset were:')
                    logging.error(list(dataset))
                    logging.error(current_path + " was not found in dataset level: " + str(len(self.splitted_path) - level))
                    # exit(1)
            elif current_path[0] == ".":
                current_path_value = current_path[1:]
                if current_path_value in list(dataset):
                    self.cross_path(dataset[current_path_value],next_path, cross_path_context = cross_path_context)
                else:
                    logging.info(list(dataset))
                    logging.error(current_path + " was not found in dataset level: " + str(len(self.splitted_path) - level))
                    # exit(1)
                    
            elif current_path[0] == "[":
                current_path_value = current_path[1:-1]
                if int(current_path_value) <= len(dataset):
                    self.cross_path(dataset[int(current_path_value)],next_path, cross_path_context = cross_path_context)
                    
                else:
                    logging.error( current_path + " was not found in dataset level: " + str(len(self.splitted_path) - level))
                    exit(1)
            
            elif current_path[0] == "{":
                item_name = current_path[1:-1]
                if level > 0:
                    if type(dataset) is dict:
                        for key,value in dataset.items():
                            next_path = path[1:]
                            # new_cross_path_context = {item_name: {"key": key, "value": value}}
                            cross_path_context = { **cross_path_context, **{item_name: {"key": key, "value": value}}}
                            self.cross_path(dataset[key],next_path,cross_path_context=cross_path_context)
                            
                    elif type(dataset) is list:
                        index = 0
                        for item in dataset:
                            next_path = path[1:]
                            # new_cross_path_context = { item_name: item }
                            cross_path_context = { **cross_path_context, **{ item_name: item }}
                            self.cross_path(dataset[index],next_path,cross_path_context=cross_path_context)
                            index += 1
                else:
                    logging.info(f"item_name: {item_name}")
                    self.render_table(dataset=dataset,select=self.select, item_name = item_name, context = cross_path_context)
            else:
                logging.info("[ERROR] was looking for path...")
                exit(1)
        else:
            item_name = path[0][1:-1]
            # logging.info(f"item_name: {item_name}")
            self.render_table(dataset=dataset,select=self.select, item_name = item_name, context=cross_path_context)
    
    def render_object(self, dataset, path="{}", select=[], unselect=[], views={}, when=[], format="", context={}, queryset={}):
        # exit(0)
        for query_item,query_data in queryset.items():
            logging.info(f"query_item: {query_item}")
            # exit(0)
            if query_item == "select":
                self.select = query_data
            elif query_item == "unselect":
                self.unselect = query_data
            elif query_item == "path":
                # logging.info(f"self.path query_data: {query_data}")
                self.path = query_data
            elif query_item == "views":
                self.views = query_data
            elif query_item == "when":
                self.when = query_data
            elif query_item == "format":
                self.format = query_data
            else:
                raise Exception(f"the queryset argument contains a non accepted key: {query_item}")
            
        self.path = path if path != "{}" else self.path
        self.select = select if select != [] and select != "" else self.select
        self.unselect = unselect if unselect != [] and unselect != "" else self.unselect
        self.views = views if views != {} else self.views
        # self.when = when if when != [] else self.when
        self.when = when if when != [] and when != "" else self.when
        logging.info(f"when: {self.when.__class__.__name__}")
        if self.when.__class__.__name__ == "str":
            self.when = self.when.split(',')
        logging.info(f"when: {self.when}")
        # exit(0)
        self.format = format if format != "" else self.format
        self.context = context
        logging.info(f"unselect: {self.unselect}")

        self.dataset = dataset
        
        for k,v in self.views.items():
            self.views = {**self.views, **{ k: '{{' + str(v) + '}}' } }

        self.splitted_path = JinjaPathSplitter().split_path(self.path)
        if self.splitted_path[0] == "['']":
            self.splitted_path[0] = "['input']"
            self.dataset = {"input": self.dataset}
        
        logging.info(f"Crossing paths")
        # for item in inspect.stack():
        #     logging.info(f"  {item[3]}")
        # self.cross_path(self.dataset, self.splitted_path, cross_path_context=self.views )
        self.cross_path(self.dataset, self.splitted_path )

        if self.format == "json":
            return json.dumps(self.json)
        elif self.format == "th":
            return self.th
        elif self.format == "td":
            return self.td
        elif self.format == "github":
            return tabulate.tabulate(self.td,self.th,tablefmt="github")
        elif self.format == "html":
            return tabulate.tabulate(self.td,self.th,tablefmt="unsafehtml")
        else:
            return tabulate.tabulate(self.td,self.th,tablefmt=self.format)
        
        # return out_return[self.format]
    
    def render_table(self, dataset, select=[], item_name='', context={}):
        stylings = []
        logging.info(f"unselect: {self.unselect}")
        if len(select) > 0:
            logging.info(f"select: {select.__class__.__name__}")
            if select.__class__.__name__ == "str":
                expressions = fields_label = select.split(",")
            else:
                expressions = [expressions['expr'] for expressions in select]
                stylings = [(stylings['styling'] if 'styling' in stylings else []) for stylings in select]
                fields_label = [fields_label['as'] for fields_label in select]
        else:
            fields = path_auto_discover().discover_paths(dataset)
            fields_label = list(map(lambda item: '.'.join(item), fields))
            item_name = 'item' if item_name == '' else item_name
            expressions = list(map(lambda item:  item_name + '[\'' + '\'][\''.join(item) + '\']' , fields))
        
        if self.unselect != [] and self.unselect != "":
            for field in self.unselect.split(','):
                if field in fields_label:
                    index = fields_label.index(field)
                    del expressions[index]
                    del fields_label[index]
                    if stylings != []:
                        del stylings[index]

        logging.info(f"expressions: {expressions}")
        logging.info(f"fields_label: {fields_label}")
        # exit()

        if type(dataset) is dict:
            dataset_to_cover = []
            for key,value in dataset.items():
                dataset_to_cover = dataset_to_cover + [ {'key': key, 'value': value} ]
        elif type(dataset) is list:
            dataset_to_cover = dataset
        else:
            raise Exception('[ERROR] dataset must be a dict or list, was: ' + str(type(dataset)))

        # static_context = {"dataset": dataset, **context}
        column_templates = []
        for expr in expressions:
            jinja_expr = '{{ ' + expr  + ' }}'
            column_templates = column_templates + [Templater(template_string=jinja_expr, static_context={**context,**self.context})]

        view_templates = []
        for var_name,var_data in self.views.items():
            view_templates = view_templates + [Templater(template_string=str(var_data), static_context={**context,**self.context})]

        when_templates = []
        for condition in self.when:
            when_templates = when_templates + [Templater(template_string=condition, static_context={**context,**self.context})]



        for item in dataset_to_cover:
            row = []
            json_dict = {}

            def when(when=[],when_context={}):
                condition_test_result = "True"
                for condition in when:
                    jinja_expr = '{{ ' + condition  + ' }}'
                    # logging.info(f"item_name: {item_name}")
                    logging.info(f"when: {when}")
                    # loop_condition_context = item
                    # loop_condition_context = { item_name: item } if item_name != '' else item
                    loop_condition_context = { item_name: item } if (item_name != '' and item_name != 'item' ) else item
                    logging.info(f"loop_condition_context: {loop_condition_context}")
                    # loop_condition_context = { item_name: item }
                    condition_template = Templater(template_string=jinja_expr, static_context= {**when_context,**loop_condition_context})
                    condition_test_result = condition_template.render({},eval_str=True,strict_undefined=False)
                    if condition_test_result == "False":
                        break
                return condition_test_result

            for expr in expressions:
                loop_context = { item_name: item } if item_name != '' else item
                view_context = {}
                view_index = 0
                for var_name,var_data in self.views.items():
                    try:
                        templated_var = view_templates[view_index].render({**loop_context,**view_context},eval_str=True,strict_undefined=False)
                    except:
                        logging.error(f"Error while rendering var_name: {var_name}, var_data: {var_data}")
                        exit(1)
                    view_context.update({ var_name: templated_var })
                    view_index += 1

            if self.when != []:
                condition_test_result = when(when = self.when, when_context = {**self.context,**context,**view_context})
            else:
                condition_test_result = "True"
            
                
            if condition_test_result == "True":
                column_index = 0
                for expr in expressions:
                    loop_context = { item_name: item } if item_name != '' else item
                    try:
                        value_for_json = value = column_templates[column_index].render({**loop_context,**view_context},eval_str=True,strict_undefined=False)
                    except:
                        break
                    del loop_context
                    if self.format == "html":
                        value = html.escape(str(value))
                    key = fields_label[column_index]
                    if value_for_json != None:
                        json_value = { key: value_for_json }
                        json_dict = {**json_dict, **json_value }
                        del json_value
                        del value_for_json
                    if stylings != []:
                        styling = stylings[column_index]
                        condition_color = "True"
                        # if styling != []:
                        for styling_attributes in styling:
                            color_conditions = [color_conditions for color_conditions in  styling_attributes['when'] ]
                            # logging.info(color_conditions)
                            condition_color = when(when = color_conditions, when_context = {**context,**view_context})
                            if condition_color == "True":
                                value = Styling().apply(value = value,format=self.format, styling_attributes = styling_attributes)
                                # logging.info(f"condition_color value: {value}")

                    row = row + [ value ]
                    del value
                    column_index += 1
                self.json = self.json + [ json_dict ]
                self.td = self.td + [ row ]
        
        
        if fields_label is None:
            headers = list(map(lambda item: '.'.join(item), expressions))
            fields_label = headers
        
        self.th = fields_label
            
        try:
            self.json_content = json.dumps(self.json)
        except Exception as error:

            logging.info(tabulate(self.td,self.th))
            logging.error(f"\nSomething wrong with json rendering, Errors was:\n  {error}")
            exit(2)

class Plugin:
    def env(var_name,**kwargs):
        if var_name not in os.environ:
            if 'default' in kwargs:
                return kwargs['default']
            else:
                raise Exception(f"Environment variable {var_name} not found")
        else:
            return os.environ[var_name]

    def shell(cmd,default=None):
        import subprocess
        
        shell_output = subprocess.check_output(cmd, shell=True,universal_newlines=True)
        return shell_output
    
        # if ms_system() == "MINGW64" or ms_system() == "CLANGARM64":
        #     bash_path = shutil.which("bash.exe")
        #     if bash_path is None:
        #         raise FileNotFoundError("bash.exe not found in PATH.")
        #     try:
        #         return subprocess.run([bash_path, "-c", cmd], check=True,universal_newlines=True)
        #         # output = subprocess.run(
        #         #     [bash_path, "-c", cmd],
        #         #     check=True,
        #         #     capture_output=True,  # Capture stdout et stderr
        #         #     text=True  # Retourne les résultats en tant que chaîne de caractères
        #         # )
        #         # return output.stdout

        #     except subprocess.CalledProcessError as error:
        #         logging.error(f"Error while running shell command: {cmd}")
        #         logging.error(f"Error was: {error}")
        #         exit(1)
        # else:
        #     shell_output = subprocess.check_output(cmd, shell=True,universal_newlines=True)
        #     return shell_output

    def load_files(search_string, format=json, ignore_errors=True):
        """
        Load multiple files from a search string
        formats in text,json,yaml
        """
        if running_os == "Windows":
            cmd = f"dir /s /b {search_string}"
            logging.info(f"cmd: {cmd}")
            files_str = os.popen("dir /s /b " + search_string).read()
        else:
            files_str = os.popen("ls -1 " + search_string).read()

        file_list_dataset = []
        for file_name_full_path in files_str.split('\n'):
            if file_name_full_path != '':
                with open(file_name_full_path, 'r') as input_yaml:
                    try:
                        file_content =  yaml.safe_load(input_yaml)
                        if running_os == "Windows":
                            sep = "\\"
                            file_path = sep.join(file_name_full_path.split('\\')[:-1])
                            file_name = file_name_full_path.split('\\')[-1]
                        else:
                            file_path = "/".join(file_name_full_path.split('/')[:-1])
                            file_name = file_name_full_path.split('/')[-1]
                        file = { 
                                "name": file_name,
                                "path": file_path,
                                "content": file_content
                                }
                        file_list_dataset = file_list_dataset + [{ **file }]
                    except Exception as error:
                        logging.warning(f"fail loading file {file_name_full_path}, skipping")
        return file_list_dataset

class path_auto_discover:
    def __init__(self):
        self.paths = []
        self.fields = []
        self.raw_rows = []
        
    def cover_paths(self,dataset,path=[]):
        if type(dataset) is dict:
            for key,value in dataset.items():
                the_path = path + [ key ]
                self.cover_paths(value,the_path )
        elif type(dataset) is list:
            if path[1:] not in self.fields:
                self.fields = self.fields + [path[1:]]
            # if len(dataset) > 0:
            #     the_path = path[:-1] + [str(path[-1]) + "[0]"]
            #     logging.info(f"path: {path[-1]}")
            #     logging.info(f"the_path: {the_path}")
            #     self.cover_paths(dataset[0], the_path)
            # else:
            #     # pass
            #     if path[1:] not in self.fields:
            #         self.fields = self.fields + [path[1:]]
        else:
            self.paths = self.paths + [ path + [dataset] ]
            if path[1:] not in self.fields:
                self.fields = self.fields + [path[1:]]

    def discover_paths(self,dataset):
        
        # when input is dict transform as list like dict2items
        if type(dataset) is dict:
            dataset_as_list = []
            for key,value in dataset.items():
                dataset_as_list = dataset_as_list + [ {'key': key, 'value': value} ]
            dataset = dataset_as_list
        index=0

        try:
            for item in dataset:
                for key,value in item.items():
                    self.cover_paths(value,[str(index),key])
                    index+=1
                self.raw_rows = self.raw_rows + [ item ]
        except(Exception) as error:
            logging.error(f"Something wrong with your dataset, error was:")
            logging.error(f"    {error}")
            exit(1)
        logging.info(f"fields: {self.fields}")
        return self.fields

class JinjaPathSplitter:

    def cover_path(self,path=""):
        if len(path) > 0:
            reference_found = "no"
            if path[0:2] == "['":
                if "']" in path:
                    left_part = path[2:].split("']")[0]
                    if left_part == "":
                        logging.info("Error dict expression empty, starting at " + str("".join(self.path_list)) )
                        exit(1)
                    else:
                        left_part = "['" + left_part + "']"
                        remaining_path = path[len(left_part):]
                        self.path_list = self.path_list + [ left_part ]
                        if remaining_path != "":
                            self.cover_path(remaining_path)
                        reference_found = "yes"
                        
                else:
                    logging.info('error expect "\']" was not found')
                    exit(1)
                
            if path[0] == ".":
                left_part = re.sub(r'^([^[^{^\.]*).*',r'.\1',path[1:])
                remaining_path = path[len(left_part):]
                self.path_list = self.path_list + [ left_part ]
                if remaining_path != "":
                    self.cover_path(remaining_path)
                
            elif path[0] == "{":
                if "}" in path:
                    left_part = re.sub(r'^([^}]*).*',r'\1}',path)
                    remaining_path = path[len(left_part):]
                    self.path_list = self.path_list + [ left_part ]
                    if remaining_path != "":
                        self.cover_path(remaining_path)
                else:
                    logging.info('error expect "}" was not found')
                    exit(1)
                    
            elif path[0] == "[":
                if reference_found == "no":
                    if "]" in path:
                        left_part = re.sub(r'^([^]]*).*',r'\1]',path)
                        remaining_path = path[len(left_part):]
                        self.path_list = self.path_list + [ left_part ]
                        if remaining_path != "":
                            self.cover_path(remaining_path)
                    else:
                        logging.info('error expect "}" was not found')
                        exit(1)
                    
            else:
                if path == "" or path[0:2] == "['" or path[0] == "{" or path[0] == ".":
                    pass
                else:
                    logging.info(path[0:2])
                    logging.info('Error don''t know to do with ' + path)
                    logging.info('Error hapenned there ' + ''.join(self.path_list))
                    exit(1)
                
    def extract_var_from_path(self,path):
        if len(path) > 0:
            left_part = re.sub(r'^([^[^\.^{]*).*',r'\1',path)
            self.path_list = [ "['" + left_part + "']" ]
            remaining_path = path[len(left_part):]
            return remaining_path
    
    def split_path(self,path=""):
        remaining_path = self.extract_var_from_path(path)
        # logging.info('debug remaining_path: ' + remaining_path)
        self.cover_path(remaining_path)
        return self.path_list

class Styling:
    def __init__(self):
        self.color_table = [{"name":"Black","ansi_code":30,"hex":"#000000"},{"name":"Red","ansi_code":31,"hex":"#FF0000"},{"name":"Green","ansi_code":32,"hex":"#008000"},{"name":"Yellow","ansi_code":33,"hex":"#FFFF00"},{"name":"Blue","ansi_code":34,"hex":"#0000FF"},{"name":"Magenta","ansi_code":35,"hex":"#FF00FF"},{"name":"Cyan","ansi_code":36,"hex":"#00FFFF"},{"name":"White","ansi_code":37,"hex":"#FFFFFF"},{"name":"Gray","ansi_code":90,"hex":"#808080"},{"name":"LightRed","ansi_code":91,"hex":"#FF8080"},{"name":"LightGreen","ansi_code":92,"hex":"#80FF80"},{"name":"LightYellow","ansi_code":93,"hex":"#FFFF80"},{"name":"LightBlue","ansi_code":94,"hex":"#8080FF"},{"name":"LightMagenta","ansi_code":95,"hex":"#FF80FF"},{"name":"LightCyan","ansi_code":96,"hex":"#80FFFF"},{"name":"LightWhite","ansi_code":97,"hex":"#F0F0F0"}]
    def view_all_colors(self):
        return self.color_table
    def get_color(self,color_name="",format=""):
        color_match=[color for color in self.color_table if color['name'].lower() == color_name.lower() ]
        # logging.info(f"color_match: {color_match}")
        # logging.info(f"color_match: {format}")
        if color_match == []:
            return ""
        else:
            if format == "html":
                color_pallet = "hex"
            elif format == "simple":
                color_pallet = "ansi_code"
            elif format == "github":
                return color_name
            else:
                return ""
        # logging.info(f"color_match: {color_match[0]}")
        return color_match[0][color_pallet]


    def apply(self,value="",format="",styling_attributes={}):
        # if format == "simple":
            # logging.info(f"style: {styling_attributes['style']}")
            if "style" in styling_attributes:
                color_label = styling_attributes['style'].split(": ")[1]
            else:
                color_label = "white"
            text_formating = 0
            formating = ""
            if "formating" in styling_attributes:
                formating = styling_attributes['formating']
            if formating == "normal" or formating == "":
                text_formating = 0
            elif formating == "bold":
                text_formating = 1
            elif formating == "dim":
                text_formating = 2
            elif formating == "italic":
                text_formating = 3
            elif formating == "underlined":
                text_formating = 4
            else:
                logging.error(f"Unknown formating: {formating}")
                exit(1)
            # color_corresp = self.get_color(color_label,"ansi_code")
            color_corresp = self.get_color(color_label,format)

            if color_corresp == "":
                if format == "html":
                    value_colorized  = r'<span style="' + styling_attributes['style'] + ';">' + value + r"</span>"
                else:
                    logging.info(f"style '{styling_attributes['style']}' not found, using default")
                    value_colorized = value

            else:
                if format == "simple":
                    value_colorized = f"\x1b[{text_formating};{color_corresp}m{value}\x1b[0m"
                elif format == "github":
                    # value_colorized = f"\x1b[{text_formating};{color_corresp}m{value}\x1b[0m"
                    # value_colorized = f"$`\textcolor{{red}}{{\text{{Smith}}`$"
                    value_colorized = r"$`\textcolor{"+ color_label + r"}{\text{" + value + "}}`$"
                elif format == "html":
                    value_colorized  = r'<span style="' + styling_attributes['style'] + r';">' + value + r"</span>"
                else:
                    value_colorized = f"\x1b[{text_formating};{color_corresp}m{value}\x1b[0m"

                logging.info(f"format: {format}")   
            return value_colorized

class Templater:
    def __init__(self, template_string = "", static_context = {}):
        if 'Environment' not in sys.modules:
            from jinja2 import Environment, StrictUndefined
        env = Environment(undefined=StrictUndefined)

        jtable_core_filters = [name[0] for name in inspect.getmembers(Filters, predicate=inspect.isfunction)]
        for filter_name in jtable_core_filters:
            env.filters[filter_name] = getattr(Filters, filter_name)
        # logging.info(f"jtable_core_filters: {jtable_core_filters}")

        ####################  Add plugin function ####################
        jtable_core_plugins = [name[0] for name in inspect.getmembers(Plugin, predicate=inspect.isfunction)]
        logging.info(f"jtable_core_plugins: {jtable_core_plugins}")
        class plugin_fct(object):
            def process_plugin(self,*args, **kwargs):
                if len(args) == 0 and len(kwargs) == 0:
                    logging.error("plugin function must have at least one argument in:")
                    exit(3)
                if args[0] not in jtable_core_plugins:
                    logging.error(f"plugin function {args[0]} not found in {', '.join(jtable_core_plugins)}")
                    exit(3)
                method_to_call = getattr(Plugin, args[0], None)
                try:
                    res = method_to_call(*args[1:],**kwargs)
                except Exception as error:
                    logging.error(f"Failed to call plugin function {args[0]}, error was:\n  {str(error)}")
                    exit(3)
                return res

            
        plugin = lambda: plugin_fct().process_plugin
        static_context = {**static_context, **{"plugin": plugin()}}

        ##############################################################
        try:
            self.template = env.from_string(template_string, globals=static_context)
        except Exception as error:
            logging.error(f"Failed to compile template, error was:\n  {str(error)}")
            exit(3)
    
    def render(self, vars, eval_str = False, strict_undefined = True):

        try:
            out_str = self.template.render(vars)
        except Exception as error:
            if str(error)[0:30] == "'dict object' has no attribute" \
                or str(error)[0:30] == "'list object' has no attribute"\
                or str(error).__contains__("is undefined"):
                if strict_undefined == True:
                    logging.error(f"Failed while rendering context, error was:\n  {str(error)}")
                    raise error
                else:
                    out = out_str =""
            else:
                out = out_str = error
                logging.error(f"Failed while rendering context, error was:\n  {str(error)}")
                raise out
            
        if eval_str == True:
            try:
                expr = ast.parse(out_str, mode='eval').body
                expr_type = expr.__class__.__name__
                if expr_type == 'List' or expr_type == 'Dict':
                    out =  ast.literal_eval(out_str)
                elif expr_type == 'Name':
                    out = out_str
                else:
                    out = str(out_str)
            except:
                out = out_str
        else:
            out = out_str
                    
        return out

def main():
    JtableCli().parse_args()
    return

if __name__ == '__main__':
    main()