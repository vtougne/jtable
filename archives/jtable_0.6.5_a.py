#!/usr/bin/env python3
import yaml, sys, json, re, os, ast, inspect, datetime, time
from os import isatty
from tabulate import tabulate



class Filters:
    def jtable(dataset,select=[],path="stdin{}",format="text"):
        from jtable import JtableCls
        return JtableCls(render="jinja_ansible").render_object({"stdin": dataset},path=path, select=select)[format]
    def from_json(str):
        return json.loads(str)
    def to_json(a, *args, **kw):
        """ Convert the value to JSON """
        return json.dumps(a, *args, **kw)
    def from_yaml_all(data):
        return yaml.safe_load_all(data)
    def type_debug(o):
        return  o.__class__.__name__

    def to_datetime(_string, format="%Y-%m-%d %H:%M:%S"):
        return datetime.datetime.strptime(_string, format)
    def strftime(string_format, second=None):
        """ return a date string using string.
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
    # print('coucou')
    # exit(0)
    def __init__(self):
        self.path = ""
        global BaseLoader,Environment
        from jinja2 import Environment, BaseLoader
        
    def parse_args(self):
        if 'JTABLE_RENDER' in os.environ:
            render=os.environ['JTABLE_RENDER']
        else:
            render="jinja_native"

        import argparse

        select = []
        format = "text"
        parser = argparse.ArgumentParser(description='Tabulate your JSON/Yaml data and transform it using Jinja')

        parser.add_argument("-q", "--query_file", help = "Show Output")
        parser.add_argument("-p", "--json_path", help = "json path")
        parser.add_argument("-f", "--format", help = "text,json,th,td")
        parser.add_argument("--inspect", action="store_true", help="inspect stdin")
        parser.add_argument("-jf", "--json_file", help = "load json")
        parser.add_argument("-jfs", "--json_files", help = "load multiple jsons")


        args = parser.parse_args()
        dataset = {}

        vars = {}
        facts = {}
        
        if args.query_file:
            with open(args.query_file, 'r') as file:
                query_set = yaml.safe_load(file)
                if 'vars' in query_set:
                    vars = query_set['vars']
                if 'select' in query_set:
                    select = query_set['select']
                if 'path' in query_set:
                    self.path = query_set['path']

        input_path_var_name="stdin"

        is_pipe = not isatty(sys.stdin.fileno())

        stdin=""
        if is_pipe:
            for line in sys.stdin:
                stdin = stdin + line
            dataset = { input_path_var_name: yaml.safe_load(stdin) }

        if not is_pipe and not args.json_file and not args.json_files and not args.query_file:
            args = parser.parse_args(['--help'])
            exit(0)

        if args.json_file:
            # err_help = "\n[ERROR] json_file must looks like this:\n\n\
            #     jtable --json_file \"{var_name_to_store}:folder_1/*/*/config.yml\"\n"
            input_path_var_name = args.json_file.split(':')[0]
            file_name = ':'.join(args.json_file.split(':')[1:])
            with open(file_name, 'r') as input_yaml:
                dataset = {**dataset, **{ input_path_var_name: yaml.safe_load(input_yaml) } }
                
        if args.json_files:
            err_help = "\n[ERROR] json_files must looks like this:\n\n\
                jtable --json_files \"{var_name_to_store}:folder_1/*/*/config.yml\"\n"
            if args.json_files[0] != "{":
                print(err_help)
                exit(1)
            else:
                splitted_path = args.json_files[1:].split('}:')
                input_path_var_name = splitted_path[0]
                path = args.json_files[len(input_path_var_name) + 3 :]
                # print("debug input_path_var_name: " + input_path_var_name )
                # print("debug path: " + path )
                # exit(0)
                files_str = os.popen("ls -1 " + path).read()
                file_list_dataset = []
                for full_file_name in files_str.split('\n'):
                    if full_file_name != '':
                        with open(full_file_name, 'r') as input_yaml:
                            file_content =  yaml.safe_load(input_yaml)
                            file_path = "/".join(full_file_name.split('/')[:-1])
                            file_name = full_file_name.split('/')[-1]
                            file = { 
                                    "name": file_name,
                                    "path": file_path,
                                    "content": file_content
                                    }
                              
                            # exit(0)
                            file_list_dataset = file_list_dataset + [{ **file }]
                dataset = {**dataset, **{ input_path_var_name: file_list_dataset } }
                # print(dataset)
                # exit(1)
        
        
        if args.json_path:
            new_path = args.json_path

            expr_end_by_braces=(re.sub('.*({).*(})$',r'\1\2',args.json_path))
            expr_path_var_name=(re.sub('^(.{' + str(len(input_path_var_name)) + '}).*$',r'\1',args.json_path))
            # print(expr_path_var_name) ; exit(0)
            if not expr_path_var_name in dataset:
                new_path =  list(dataset)[0] + "." + new_path

            if expr_end_by_braces != "{}":
                new_path = new_path + "{}"
            self.path = new_path

        if self.path == "":
            if "stdin" in dataset:
                self.path = "stdin{}"
            else:
                self.path = list(dataset)[0]
        
        
        if args.format:
            format = args.format
        

                    
        if args.inspect:
            inspected_paths = Inspect().view_paths(dataset)
            tbl = tabulate(inspected_paths,['path','value'])
            print(tbl)
            exit(0)


        if args.query_file:
            with open(args.query_file, 'r') as file:
                query_set = yaml.safe_load(file)
                if 'facts' in query_set:
                    # dataset = query_set['facts']
                    facts = {}
                    for key,value in query_set['facts'].items():
                        # print(value)
                        # print(list(dataset))
                        jinja_eval = JtableCls().jinja_render_value(str(value),dataset)
                        # print(jinja_eval)
                        facts.update({key: jinja_eval})
                        dataset = {**dataset,**facts}
                    dataset = facts
                    # print('dataset first keys')
                    # print(dataset)
                    # print(list(dataset))
        # print(dataset)
        # exit(1)

        out = JtableCls(render=render).render_object(dataset,path=self.path,select=select,vars=vars)[format]
        print(out)


class JtableCls:
    def __init__(self, render="jinja_native"):
        self.td = []
        self.th = []
        self.table_headers = []
        self.json = []
        self.render = render
        self.splitted_path = []

        if self.render == "jinja_ansible":
            global Templar,AnsibleContext,AnsibleEnvironment
            from ansible.template import Templar,AnsibleContext,AnsibleEnvironment
            from ansible.parsing.dataloader import DataLoader
            self.loader = DataLoader()
        else:
            self.loader=BaseLoader()
    
    def cross_path(self,dataset,path,context={}):
        level = len(path)
        if level > 0:
            next_path = path[1:]
            current_path = str(path[0])
            current_path_value = "unknown"
            current_path_value = current_path_value
            if current_path[0:2] == "['":
                current_path_value = current_path[2:-2]
                if current_path_value in list(dataset):
                    self.cross_path(dataset[current_path_value],next_path, context = context)
                else:
                    print('key dataset were:')
                    print(list(dataset))
                    print("ERROR " + current_path + " was not found in dataset level: " + str(len(self.splitted_path) - level))
                    exit(1)
            elif current_path[0] == ".":
                current_path_value = current_path[1:]
                if current_path_value in list(dataset):
                    self.cross_path(dataset[current_path_value],next_path, context = context)
                else:
                    print(list(dataset))
                    print("ERROR " + current_path + " was not found in dataset level: " + str(len(self.splitted_path) - level))
                    exit(1)
                    
            elif current_path[0] == "[":
                current_path_value = current_path[1:-1]
                # print('debug typ dataset: ' + str(type(dataset)))
                # print('debug dataset: ' + str(dataset))
                
                if int(current_path_value) <= len(dataset):
                    self.cross_path(dataset[int(current_path_value)],next_path, context = context)
                    
                else:
                    print("ERROR " + current_path + " was not found in dataset level: " + str(len(self.splitted_path) - level))
                    exit(1)
            
            elif current_path[0] == "{":
                item_name = current_path[1:-1]
                if level > 1:
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
                    self.render_table(dataset,select=self.select, item_name = item_name, context = context)
            else:
                print("[ERROR] was looking for path...")
                exit(1)
                
            
        else:
            # print('last path: ' + str(dataset))
            self.render_table(dataset,select=self.select,context=context)
        # print('debug path count': + str(len(paths)))
    
    def render_object(self,dataset,path="stdin{}",select=[],vars={}):
        self.dataset = dataset
        
        self.select = select
        self.vars = vars
        
        self.splitted_path =   JinjaPathSplitter().split_path(path)
        
        # print('debug path: ' + str(path))
        # print('debug self.splitted_path: ' + str(self.splitted_path))
        # self.cross_path_old()
        
        
        self.cross_path(dataset,self.splitted_path )

        # exit(0)
            
        out_return = {
            "th": self.th,
            "td": self.td,
            "text": tabulate(self.td,self.th),
            "json": self.json_content
        }
        return out_return

    def jinja_render_value(self,template,context):
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
                    print("[ERROR] error while jinja_ansible rendering value, error was: " + str(error))
        else:
            try:
                tenv = Environment(extensions=['jinja2_ansible_filters.AnsibleCoreFiltersExtension'])
            except:
                tenv = Environment(loader=self.loader)
                jtable_core_filters = [name for name, func in inspect.getmembers(Filters, predicate=inspect.isfunction)]
                for filter_name in jtable_core_filters:
                    tenv.filters[filter_name] = getattr(Filters, filter_name)
                
            try:
                mplate = tenv.from_string(template)
            except Exception as error:
                sys.stderr.write("[ERROR] while loading env template: " + str(template) + "\n" )
                sys.stderr.write("[ERROR] error was: " + str(error) + "\n" )
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
                    sys.stderr.write("[ERROR] error while jinja_native rendering value, error was: " + str(context) + "\n" )
                    sys.stderr.write("[ERROR] error while rendering context: \nb" + str(error) + "\n" )
                    exit(1)
            if out_str == "":
                out = None
            else:
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
        return out
    
    def render_table(self,dataset,select=[],item_name = '',context={}):
        if len(select) > 0:
            expressions = [expressions['expr'] for expressions in select]
            fields_label = [fields_label['as'] for fields_label in select]
        else:
            fields = path_auto_discover().discover_paths(dataset)
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
            print(dataset)
            raise Exception('[ERROR] dataset must be a dict or list, was: ' + str(type(dataset)))

            
        for item in dataset_to_cover:
            row = []
            json_dict = {}
            row_index = 0
            for expr in expressions:
                jinja_expr = '{{ ' + expr  + ' }}'
                loop_context = { item_name: item } if item_name != '' else item
                context = { **context, **loop_context, **self.dataset}
                # print(context)
                # exit(0)
                rendered_context = {}
                for var_name,var_data in self.vars.items():
                    # print('debug type: ' + str(type(var_data)))
                    # if type(dataset) is dict:
                    #     var_data = str(var_data)
                    templated_var = self.jinja_render_value(template=str(var_data), context = context)
                    rendered_context.update({var_name: templated_var })
                # exit(1)
                # print('debug rendered_context: ' + str(rendered_context))
                
                value_for_json = value = self.jinja_render_value( template = jinja_expr, context = {**context,**rendered_context})

                if value_for_json != None:
                    key = fields_label[row_index]
                    json_value = { key: value_for_json }
                    json_dict = {**json_dict, **json_value }
                    del json_value
                    del value_for_json
                    
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
            print("\nERROR!!  sometinh wrong with json rendering, tabme maight contains the error \nErrors was:")
            print(error)
            exit(2)


class FilterModule(object):
  """ Ansible core jinja2 filters """
  
  def filters(self):
    return {
      'jtable': jtable_filter
    }


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
            index=0
            for item in dataset:
                self.cover_paths(item,path)
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

def main():
    JtableCli().parse_args()


if __name__ == '__main__':
    main