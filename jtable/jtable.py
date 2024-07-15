#!/usr/bin/env python3
import yaml, sys, json, re, os, ast, inspect, datetime, time, logging, logging.config
from os import isatty
from tabulate import tabulate
# tabulate.PRESERVE_WHITESPACE = True
# import tabulate

from typing import Any, Dict, Optional

class _ExcludeErrorsFilter(logging.Filter):
    def filter(self, record):
        """Only lets through log messages with log level below ERROR ."""
        return record.levelno < logging.ERROR

"""
https://stackoverflow.com/questions/14058453/making-python-loggers-output-all-messages-to-stdout-in-addition-to-log-file
"""
logging_config = {
    'version': 1,
    'filters': {
        'exclude_errors': {
            '()': _ExcludeErrorsFilter
        }
    },
    'formatters': {
        'my_formatter': {
            'format': '%(asctime)s (line %(lineno)s) | %(levelname)s %(message)s',
            'datefmt': '%H:%M:%S'

        }
    },
    'handlers': {
        'console_stderr': {
            'class': 'logging.StreamHandler',
            'level': 'ERROR',
            'formatter': 'my_formatter',
            'stream': sys.stderr
        },
        'console_stdout': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'my_formatter',
            'filters': ['exclude_errors'],
            'stream': sys.stderr
        },
    },
    'root': {
        'level': 'NOTSET',
        'handlers': ['console_stderr', 'console_stdout']
    },
}

logging.config.dictConfig(logging_config)

class Filters:
    def jtable(dataset,select=[],path="{}",format="",vars={}, when=[],queryset={}):
        # logging.info(f"path: {path}")
        # return JtableCls().render_object( dataset,path=path, select=select,vars=vars, when=when,format=format, queryset=queryset)[format]
        return JtableCls().render_object( dataset,path=path, select=select,vars=vars, when=when,format=format, queryset=queryset)
        # return JtableCls().render_object({"stdin": dataset},path=path, select=select,vars=vars)[format]
    def from_json(str):
        return json.loads(str)
    def from_yaml(data):
        return yaml.safe_load(data)
    def from_yaml_all(data):
        return yaml.safe_load_all(data)
    def intersect(a, b):
        # logging.info(b)
        # return set(a).intersection(b)
        return list(set(a).intersection(b))
    def to_json(a, *args, **kw):
        """ Convert the value to JSON """
        return json.dumps(a, *args, **kw)
    def to_yaml(v):
        """ Convert the value to JSON """
        return yaml.dump(v, allow_unicode=True)
    
    def type_debug(o):
        return  o.__class__.__name__

    def to_datetime(_string, format="%Y-%m-%d %H:%M:%S"):
        return datetime.datetime.strptime(_string, format)
    def strftime(string_format, second=None):
        """ return a date string using string.
        timestamp  option strftime(s) Doesn't works on cygwin => old known cygwin issue
        See https://docs.python.org/2/library/time.html#time.strftime for format """
        if second is not None:
            try:
                second = int(second)
            except Exception:
                raise "Invalid value for epoch value (%s)" % second
        return time.strftime(string_format, time.localtime(second))
    
    def regex_replace(value="", pattern="", replacement="", ignorecase=False):
        """ Perform a `re.sub` returning a string """
        if ignorecase:
            flags = re.I
        else:
            flags = 0
        _re = re.compile(pattern, flags=flags)
        return _re.sub(replacement, value)

class Inspect:
    def __init__(self):
        self.out = []
    def add_row(self,row):
        self.out = self.out + [ [row[0][1:]] + [row[1]] ]
    def view_paths(self,dataset):
        self.cover_data(dataset)
        return self.out
    def cover_data(self,dataset,path=""):
        if type(dataset) is dict:
            for key,value in dataset.items():
                if " " in str(key):
                    the_path = path + "['" + str(key) + "']"
                else:
                    the_path = path + "." + str(key)
                self.cover_data(value,the_path )
        elif type(dataset) is list:
            index=0
            for item in dataset:
                the_path = path + "[" + str(index) + "]"
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
        facts = {}
        queryset = {}
        self.tabulate_var_name="stdin"
        if 'JTABLE_RENDER' in os.environ:
            render=os.environ['JTABLE_RENDER']
        else:
            render="jinja_native"

        import argparse

        parser = argparse.ArgumentParser(description='Tabulate your JSON/Yaml data and transform it using Jinja')

        parser.add_argument("-q", "--query_file", help = "Show Output")
        parser.add_argument("-p", "--json_path", help = "json path")
        parser.add_argument("-f", "--format", help = "text,json,th,td")
        parser.add_argument("--inspect", action="store_true", help="inspect stdin")
        parser.add_argument("-jf", "--json_file", help = "load json")
        parser.add_argument("-jfs", "--json_files",action='append', help = "load multiple Json's")
        parser.add_argument("-yfs", "--yaml_files", help = "load multiple Yaml's")
        parser.add_argument("-vq", "--view_query", action="store_true", help = "View query")


        args = parser.parse_args()
        
        if args.query_file:
            with open(args.query_file, 'r') as file:
                try:
                    query_file = yaml.safe_load(file)
                except Exception as error:
                    logging.error(f"Fail to load query file {args.query_file}, check Yaml format")
                    logging.error(f"error was:\n{error}")
                    exit(2)
                
            if 'queryset' in query_file:
                queryset = query_file['queryset']
                
        is_pipe = not isatty(sys.stdin.fileno())

        stdin=""
        if is_pipe:
            for line in sys.stdin:
                stdin = stdin + line
            self.dataset = { self.tabulate_var_name: yaml.safe_load(stdin) }
            # self.dataset = yaml.safe_load(stdin)

        if not is_pipe and not args.json_file and not args.json_files and not args.query_file:
            args = parser.parse_args(['--help'])
            exit(1)

        if args.json_file:
            self.tabulate_var_name = args.json_file.split(':')[0]
            file_name = ':'.join(args.json_file.split(':')[1:])
            with open(file_name, 'r') as input_yaml:
                self.dataset = {**self.dataset, **{ self.tabulate_var_name: yaml.safe_load(input_yaml) } }
                
        # logging.info(f"queryset['path']: {queryset['path']}") ; exit(0)
                
        def load_multiple_inputs(input,format):
            err_help = f"\n[ERROR] {format}_files must looks like this:\n\n\
                jtable --{format}_files \"{{target_var_name}}:folder_1/*/*/config.yml\"\n"
            if input[0] != "{":
                logging.error(err_help)
                exit(1)
            else:
                splitted_path = input[1:].split('}:')
                self.tabulate_var_name = splitted_path[0]
                # print(tabulate_var_name) ; exit(0)
                path = input[len(self.tabulate_var_name) + 3 :]
                files_str = os.popen("ls -1 " + path).read()
                # for windows syntax will be --> # dir /s /b data\*config.yml
                file_list_dataset = []
                for file_name_full_path in files_str.split('\n'):
                    if file_name_full_path != '':
                        with open(file_name_full_path, 'r') as input_yaml:
                            try:
                                file_content =  yaml.safe_load(input_yaml)
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
                # print(file) ; exit(0)
                load_multiple_inputs(file,"json")
        
        if args.json_path:
            new_path = args.json_path
            expr_end_by_braces=(re.sub('.*({).*(})$',r'\1\2',args.json_path))
            if expr_end_by_braces != "{}":
                new_path = new_path + "{}"
            queryset['path'] = new_path

        if args.query_file:
            if 'context' in query_file:
                context = {}
                for key,value in query_file['context'].items():
                    jinja_eval = JtableCls().jinja_render_value(str(value),self.dataset)
                    context.update({key: jinja_eval})
                    self.dataset = {**self.dataset,**context, **{"context": context}}

        if 'select' in queryset:
            select = queryset['select']

        if not 'path' in queryset:
            queryset['path'] = "{}"
                    
        if not "format" in queryset:
            queryset['format'] = 'text'

        if args.format:
            queryset['format'] = args.format

        if args.view_query:
            queryset['format'] = "th"
            
        # def out_expr_fct(select,path,format):
            # return "{{ " + self.tabulate_var_name + " | jtable(queryset=queryset) }}"
            
        # out_expr = out_expr_fct(str(select), queryset['path'] , queryset['format'])
        out_expr = "{{ " + self.tabulate_var_name + " | jtable(queryset=queryset) }}"
        # print(out_expr) ; exit(0)
        if args.query_file:
            if 'out' in query_file:
                out_expr = query_file['out']
            
        if args.inspect:
            inspected_paths = Inspect().view_paths(self.dataset[self.tabulate_var_name])
            tbl = tabulate(inspected_paths,['path','value'])
            print(tbl)
            return
        
        # out = JtableCls().jinja_render_value(str(out_expr),{**self.dataset,**queryset})
        # print(queryset)
        # return
        
        if args.view_query:
            # queryset['format'] = "json"
            out = JtableCls().jinja_render_value(out_expr,{**self.dataset,**{"queryset": queryset}},eval_str=True)
            # print(out)
            # return
            query_file_out = {}
            query_set_out = {}
            fields = out
            if select == []:
                for field in fields:
                    select = select + [ {'as': field, 'expr':field }  ]
            query_set_out['select'] = select
            query_set_out['path'] = queryset['path']
            # query_file_out['queryset'] = query_set_out
            query_file_out['queryset'] = query_set_out
            # query_file_out['out'] = out_expr_fct('select', queryset['path'] , 'text')
            query_file_out['out'] = out_expr
            yaml_query_out = yaml.dump(query_file_out, allow_unicode=True,sort_keys=False)
            print(yaml_query_out)
        else:
            # logging.info(f"queryset: {queryset}")
            out = JtableCls().jinja_render_value(out_expr,{**self.dataset,**{"queryset": queryset}},eval_str=True)
            # out = JtableCls().jinja_render_value(out_expr,{**self.dataset,**queryset},eval_str=False)
            # if queryset['format'] == "json":
            #     print(json.dumps(out))
            # else:
            #     print(out)
            print(out)

class JtableCls:
    def __init__(self, render="jinja_native"):
        self.td = []
        self.th = []
        self.table_headers = []
        self.json = []
        self.render = render
        self.splitted_path = []
        self.when = []
        self.select = []
        self.vars = {}
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
    
    def cross_path(self,dataset,path,context={}):
        level = len(path)
        if level > 1:
            # logging.info(f"path: {path}")
            next_path = path[1:]
            current_path = str(path[0])
            current_path_value = "unknown"
            current_path_value = current_path_value
            if current_path[0:2] == "['":
                current_path_value = current_path[2:-2]
                if current_path_value in list(dataset):
                    self.cross_path(dataset[current_path_value],next_path, context = context)
                else:
                    logging.error('keys dataset were:')
                    logging.error(list(dataset))
                    logging.error("ERROR " + current_path + " was not found in dataset level: " + str(len(self.splitted_path) - level))
                    exit(1)
            elif current_path[0] == ".":
                current_path_value = current_path[1:]
                if current_path_value in list(dataset):
                    self.cross_path(dataset[current_path_value],next_path, context = context)
                else:
                    print(list(dataset))
                    logging.error(current_path + " was not found in dataset level: " + str(len(self.splitted_path) - level))
                    exit(1)
                    
            elif current_path[0] == "[":
                current_path_value = current_path[1:-1]
                if int(current_path_value) <= len(dataset):
                    self.cross_path(dataset[int(current_path_value)],next_path, context = context)
                    
                else:
                    print("ERROR " + current_path + " was not found in dataset level: " + str(len(self.splitted_path) - level))
                    exit(1)
            
            elif current_path[0] == "{":
                item_name = current_path[1:-1]
                if level > 0:
                    if type(dataset) is dict:
                        for key,value in dataset.items():
                            next_path = path[1:]
                            new_context = {item_name: {"key": key, "value": value}}
                            context = { **context, **new_context}
                            self.cross_path(dataset[key],next_path,context=context)
                            
                    elif type(dataset) is list:
                        index = 0
                        for item in dataset:
                            next_path = path[1:]
                            new_context = { item_name: item }
                            context = { **context, **new_context}
                            self.cross_path(dataset[index],next_path,context=context)
                            index += 1
                else:
                    logging.info(f"item_name: {item_name}")
                    self.render_table(dataset=dataset,select=self.select, item_name = item_name, context = context)
            else:
                print("[ERROR] was looking for path...")
                exit(1)
        else:
            item_name = path[0][1:-1]
            # logging.info(f"item_name: {item_name}")
            self.render_table(dataset=dataset,select=self.select, item_name = item_name, context=context)
    
    def render_object(self,dataset,path="{}",select=[],vars={}, when=[],format="",queryset={}):
        for query_item,query_data in queryset.items():
            if query_item == "select":
                self.select = query_data
            elif query_item == "path":
                # logging.info(f"self.path query_data: {query_data}")
                self.path = query_data
            elif query_item == "vars":
                self.vars = query_data
            elif query_item == "when":
                self.when = query_data
            elif query_item == "format":
                self.format = query_data
            else:
                raise Exception(f"the queryset argument contains a non accepted key: {query_item}")
                # print('query_item: ' + query_item)
                # exit(1)
                # err = f"the queryset argument contains a non accepted key: {query_item}"
                # raise err
                # print('coucou')
            
            
        self.path = path if path != "{}" else self.path
        self.select = select if select != [] else self.select
        self.vars = vars if vars != {} else self.vars
        self.when = when if when != [] else self.when
        self.format = format if format != "" else self.format

        # logging.info(f"self.vars: {self.vars}")

        self.dataset = dataset

        # logging.info(f"self.select: {self.select}")
        
        for k,v in self.vars.items():
            self.vars = {**self.vars, **{ k: '{{' + str(v) + '}}' } }
            

        self.splitted_path = JinjaPathSplitter().split_path(self.path)
        # logging.info(f"self.splitted_path: {self.splitted_path}")
        if self.splitted_path[0] == "['']":
            self.splitted_path[0] = "['input']"
            # logging.info(f"self.splitted_path: {self.splitted_path}")
            self.dataset = {"input": self.dataset}
            
            
        self.cross_path(self.dataset, self.splitted_path, context=self.vars )
        
        # self.render_table(dataset=dataset,select=self.select,item_name="item")
        
        
        # self.cross_path(self.dataset, self.splitted_path )

        out_return = {
            "th": self.th,
            "td": self.td,
            "text": tabulate(self.td,self.th,tablefmt="simple"),
            "json": json.dumps(self.json)
            # "json": self.json
        }
        
        print(self.format)
        
        return out_return[self.format]

    def jinja_render_value(self,template,context,eval_str=True):

        if self.render == "jinja_ansible":
            templar = Templar(loader=self.loader, variables = context)
            
            try:
                out = templar.template(template)
            except Exception as error:
                if str(error)[0:30] == "'dict object' has no attribute":
                    out = None
                elif str(error)[0:30] == "'list object' has no attribute":
                    out = None
                else:
                    out = error
                    logging.error("Failed while jinja_ansible rendering value, error was: " + str(error))
        else:
            try:
                mplate = self.tenv.from_string(template)
            except Exception as error:
                logging.error("Failed while loading env template: " + str(template) )
                logging.error("Rrror was: " + str(error))
                exit(1)
                
            try:
                out_str =  mplate.render(**context)
            except Exception as error:
                if str(error)[0:30] == "'dict object' has no attribute":
                    out = out_str =""
                elif str(error)[0:30] == "'list object' has no attribute":
                    out = out_str =""
                else:
                    out = error
                    # logging.error("Failed while jinja_native rendering value, context was:\n" + str(context) + "\n" )
                    logging.error("Failed while rendering context: \nb" + str(error) + "\n" )
                    # exit(1)
                    raise out
            if out_str == "":
                out = None
            else:
                if eval_str == True:
                    try:
                        expr = ast.parse(out_str, mode='eval').body
                        expr_type = expr.__class__.__name__
                        if expr_type == 'List' or expr_type == 'Dict':
                            out =  ast.literal_eval(mplate.render(**context))
                        elif expr_type == 'Name':
                            out = out_str
                        else:
                            out = str(out_str)
                    except:
                        out = out_str
                else:
                    out = out_str
        return out
    
    def render_table(self,dataset,select=[],item_name = '',context={}):
        cell_stylings = None
        if len(select) > 0:
            expressions = [expressions['expr'] for expressions in select]
            cell_stylings = [(cell_stylings['styling'] if 'styling' in cell_stylings else []) for cell_stylings in select]
            fields_label = [fields_label['as'] for fields_label in select]
        else:
            fields = path_auto_discover().discover_paths(dataset)
            # print(fields) ; exit(0)
            fields_label = list(map(lambda item: '.'.join(item), fields))
            # expressions = list(map(lambda item:  'item[\'' + '\'][\''.join(item) + '\']' , fields))
            item_name = 'item' if item_name == '' else item_name
            expressions = list(map(lambda item:  item_name + '[\'' + '\'][\''.join(item) + '\']' , fields))
            
        if type(dataset) is dict:
            dataset_to_cover = []
            for key,value in dataset.items():
                dataset_to_cover = dataset_to_cover + [ {'key': key, 'value': value} ]
        elif type(dataset) is list:
            dataset_to_cover = dataset
        else:
            # print('[ERROR] dataset must be a dict or list, was: ' + str(type(dataset)))
            # print(dataset)
            raise Exception('[ERROR] dataset must be a dict or list, was: ' + str(type(dataset)))

            
        for item in dataset_to_cover:
            row = []
            json_dict = {}
            row_index = 0
            # logging.info(f"item: {item}")

            def when(when=[],context={}):
                condition_test_result = "True"
                for condition in when:
                    jinja_expr = '{{ ' + condition  + ' }}'
                    loop_condition_context = { item_name: item } if item_name != '' else item
                    context = { **context, **loop_condition_context, **self.dataset}
                    condition_context = {}
                    for var_name,var_data in self.vars.items():
                        templated_var = self.jinja_render_value(template=str(var_data), context = context)
                        condition_context.update({var_name: templated_var })
                    condition_test_result = self.jinja_render_value( template = jinja_expr, context = {**context,**condition_context})
                    # print(condition_test_result)
                    if condition_test_result == "False":
                        break
                return condition_test_result

            condition_test_result = when(when = self.when, context = context)
            
            # logging.error(f"condition_test_result: {condition_test_result}")
            # exit()
            
                
            if condition_test_result == "True":
                for expr in expressions:
                    jinja_expr = '{{ ' + expr  + ' }}'
                    loop_context = { item_name: item } if item_name != '' else item
                    context = { **context,  **self.dataset}
                    rendered_context = {}
                    for var_name,var_data in self.vars.items():
                        templated_var = self.jinja_render_value(template=str(var_data), context = {**context,**loop_context})
                        rendered_context.update({var_name: templated_var })
                    value_for_json = value = self.jinja_render_value( template = jinja_expr, context = {**context,**loop_context,**rendered_context})
                    del loop_context

                    key = fields_label[row_index]
                    if value_for_json != None:
                        json_value = { key: value_for_json }
                        json_dict = {**json_dict, **json_value }
                    # else:
                    #     json_dict = {**json_dict, **{key: None} }
                        del json_value
                    # value_for_json = undefined
                        del value_for_json


                    if cell_stylings is not None:
                        cell_styling = cell_stylings[row_index]
                        condition_color = "True"
                        if cell_styling != []:
                            for style in cell_styling:
                                color_conditions = [color_conditions for color_conditions in  style['when'] ]
                                # print(color_conditions)
                                condition_color = when(when = color_conditions, context = context)
                                if condition_color == "True":
                                    # print(style)
                                    stylized_value = Styling().apply(value = value,format="text", style = style['style'] )
                                    value = stylized_value
                        # logging.info(str(condition_color) + " / " + str(value))



                    row = row + [ value ]
                    del value
                    row_index += 1
                self.json = self.json + [ json_dict ]
                self.td = self.td + [ row ]
        
        
        if fields_label is None:
            headers = list(map(lambda item: '.'.join(item), expressions))
            fields_label = headers
        
        self.th = fields_label
            
        try:
            self.json_content = json.dumps(self.json)
        except Exception as error:

            print(tabulate(self.td,self.th))
            print("\nERROR!!  something wrong with json rendering, tabme maight contains the error \nErrors was:")
            print(error)
            exit(2)

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
            # pass
            if len(dataset) > 0:
                index=0
                for item in dataset:
                    self.cover_paths(item,path)
            else:
                if path[1:] not in self.fields:
                    self.fields = self.fields + [path[1:]]
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
        except (AttributeError, TypeError):
            print("ERROR Something wrong with your dataset")
            exit(1)

        return self.fields

class JinjaPathSplitter:

    def cover_path(self,path=""):
        if len(path) > 0:
            reference_found = "no"
            if path[0:2] == "['":
                if "']" in path:
                    left_part = path[2:].split("']")[0]
                    if left_part == "":
                        print("Error dict expression empty, starting at " + str("".join(self.path_list)) )
                        exit(1)
                    else:
                        left_part = "['" + left_part + "']"
                        remaining_path = path[len(left_part):]
                        self.path_list = self.path_list + [ left_part ]
                        if remaining_path != "":
                            self.cover_path(remaining_path)
                        reference_found = "yes"
                        
                else:
                    print('error expect "\']" was not found')
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
                    print('error expect "}" was not found')
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
                        print('error expect "}" was not found')
                        exit(1)
                    
            else:
                if path == "" or path[0:2] == "['" or path[0] == "{" or path[0] == ".":
                    pass
                else:
                    print(path[0:2])
                    print('Error what know to do with ' + path)
                    print('Error hapenned there ' + ''.join(self.path_list))
                    exit(1)
                
    def extract_var_from_path(self,path):
        if len(path) > 0:
            left_part = re.sub(r'^([^[^\.^{]*).*',r'\1',path)
            self.path_list = [ "['" + left_part + "']" ]
            remaining_path = path[len(left_part):]
            return remaining_path
    
    def split_path(self,path=""):
        remaining_path = self.extract_var_from_path(path)
        # print('debug remaining_path: ' + remaining_path)
        self.cover_path(remaining_path)
        return self.path_list

class Styling:
    def __init__(self):
        self.color_table = [{"name":"Black","ansi_code":30,"hex":"#000000"},{"name":"Red","ansi_code":31,"hex":"#FF0000"},{"name":"Green","ansi_code":32,"hex":"#008000"},{"name":"Yellow","ansi_code":33,"hex":"#FFFF00"},{"name":"Blue","ansi_code":34,"hex":"#0000FF"},{"name":"Magenta","ansi_code":35,"hex":"#FF00FF"},{"name":"Cyan","ansi_code":36,"hex":"#00FFFF"},{"name":"White","ansi_code":37,"hex":"#FFFFFF"},{"name":"Gray","ansi_code":90,"hex":"#808080"},{"name":"LightRed","ansi_code":91,"hex":"#FF8080"},{"name":"LightGreen","ansi_code":92,"hex":"#80FF80"},{"name":"LightYellow","ansi_code":93,"hex":"#FFFF80"},{"name":"LightBlue","ansi_code":94,"hex":"#8080FF"},{"name":"LightMagenta","ansi_code":95,"hex":"#FF80FF"},{"name":"LightCyan","ansi_code":96,"hex":"#80FFFF"},{"name":"LightWhite","ansi_code":97,"hex":"#F0F0F0"}]
    
    def get_color(self,color_name="",format=""):
        return [color for color in self.color_table if color['name'].lower() == color_name.lower() ][0][format]

    def apply(self,value="",format="",style=""):
        if format == "text":
            style_name = style.split(': ')[0]
            style_value = style.split(': ')[1]
            if "color" in style_name:
                color_value = self.get_color(style_value,"ansi_code")
                value_colorized = f"\x1b[1;{color_value}m{value}\x1b[0m"
                return value_colorized

def main():
    JtableCli().parse_args()
    return

# class Undefined:
#     def __repr__(self):
#         return "undefined"

#     def __str__(self):
#         return self.__repr__()

    

    
if __name__ == '__main__':
    main()
