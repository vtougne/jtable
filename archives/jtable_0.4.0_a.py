#!/usr/bin/env python3
import yaml, sys, json, re, os, ast
from os import isatty

# from jinja2 import Environment, BaseLoader
from tabulate import tabulate


try:
    from ansible.template import Templar,AnsibleContext,AnsibleEnvironment
    from ansible.parsing.dataloader import DataLoader
except:
    pass

try: 
    from jinja2 import Environment, BaseLoader
except:
    pass

global path
global path_var_name
path_var_name = "stdin"
global path_loop_var
path_loop_var = "{}"
path = path_var_name + path_loop_var

def ansible_filter(dataset,select=[]):
    return jtable_cls().render_object(dataset,path=path,select=select)


class Inspect:
    def __init__(self):
        self.out = []
    def add_row(self,row):
        self.out = self.out + [ row ]
    def view_paths(self,dataset):
        self.cover_data(dataset)
        # return('\n'.join(self.out))
        return self.out
    def cover_data(self,dataset,path=""):
        if type(dataset) is dict:
            for key,value in dataset.items():
                the_path = path + "['" + str(key) + "']"
                self.cover_data(value,the_path )
        elif type(dataset) is list:
            index=0
            for item in dataset:
                the_path = path + "[" + str(index) + "]"
                index += 1
                self.cover_data(item,the_path)
        else:
            self.add_row([path] + [str(dataset)])

class jtable_cli:
    def __init__(self):
        self.path = path
        
    def parse_args(self):
        if 'JTABLE_RENDER' in os.environ:
            render=os.environ['JTABLE_RENDER']
        else:
            render="jinja_native"

        import argparse

        select = []
        format="text"
        parser = argparse.ArgumentParser(description='Tabulate your JSON/Yaml data and transform it using Jinja')

        parser.add_argument("-q", "--query_file", help = "Show Output")
        parser.add_argument("-p", "--json_path", help = "json path")
        parser.add_argument("-f", "--format", help = "text,json,th,td")
        parser.add_argument("--inspect", action="store_true", help="inspect stdin")
        parser.add_argument("-jf", "--json_file", help = "load json")
        parser.add_argument("-jfs", "--json_files", help = "load multiple jsons")


        args = parser.parse_args()
        dataset = {}
        path_var_name="stdin"

        is_pipe = not isatty(sys.stdin.fileno())
        
        stdin=""
        if is_pipe:
            for line in sys.stdin:
                stdin = stdin + line

            dataset = { path_var_name: yaml.safe_load(stdin) }
        # dataset = {**dataset, **{ path_var_name: yaml.safe_load(stdin) } }
        
        if args.json_file:
            input_path_var_name = args.json_file.split(':')[0]
            file_name = ':'.join(args.json_file.split(':')[1:])
            with open(file_name, 'r') as input_yaml:
                # dataset = { path_var_name: yaml.safe_load(input_yaml) }
                dataset = {**dataset, **{ input_path_var_name: yaml.safe_load(input_yaml) } }
                
        if args.json_files:
            path_var_name = args.json_file.split(':')[0]
            file_name = ':'.join(args.json_file.split(':')[1:])
            with open(file_name, 'r') as input_yaml:
                dataset = { path_var_name: yaml.safe_load(input_yaml) }
                
        if args.json_path:
            new_path = args.json_path
            # if path is not erminated by {} or {something} then adding {} at the end
            expr_end_by_braces=(re.sub('.*({).*(})$',r'\1\2',args.json_path))
            expr_path_var_name=(re.sub('^(.{' + str(len(path_var_name)) + '}).*$',r'\1',args.json_path))
            if expr_path_var_name != path_var_name:
                new_path = path_var_name + '.' + new_path
                
            if expr_end_by_braces != "{}":
                new_path = new_path + "{}"
                
            self.path = new_path
            # print('debug path_var_name: ' + path_var_name)
            # print('debug self.path: ' + self.path)
            # exit(0)
            
        if args.format:
            format = args.format
        
        if args.query_file:
            with open(args.query_file, 'r') as file:
                query_set = yaml.safe_load(file)
                if 'select' in query_set:
                    select = query_set['select']
                    
        if args.inspect:
            inspected_paths = Inspect().view_paths(dataset)
            tbl = tabulate(inspected_paths,['path','value'])
            print(tbl)
            exit(0)
            
        print(jtable_cls(render=render).render_object(dataset,path=self.path,select=select)[format])


class jtable_cls:
    def __init__(self, render):
        self.td = []
        self.th = []
        self.table_headers = []
        self.json = []
        self.render = render
        self.splitted_path = []

        if self.render == "jinja_ansible":
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
                    print("ERROR " + current_path + " was not found in dataset level: " + str(len(self.splitted_path) - level))
                    exit(1)
            elif current_path[0] == ".":
                current_path_value = current_path[1:]
                if current_path_value in list(dataset):
                    self.cross_path(dataset[current_path_value],next_path, context = context)
                else:
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
            print('last path: ' + str(dataset))
            self.render_table(dataset,select=self.select,context=context)
        # print('debug path count': + str(len(paths)))
        

    
    def render_object(self,dataset,path=path,select=[]):
        self.dataset = dataset
        self.select = select
        
        self.splitted_path =   path_splitter().split_path(path)
        
        print('debug path: ' + str(path))
        print('debug self.splitted_path: ' + str(self.splitted_path))
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
            tenv = Environment(loader=self.loader)
            mplate = tenv.from_string(template)
            try:
                out_str =  mplate.render(**context)
            except Exception as error:
                if str(error)[0:30] == "'dict object' has no attribute":
                    out = out_str =""
                elif str(error)[0:30] == "'list object' has no attribute":
                    out = out_str =""
                else:
                    out = error
                    print("[ERROR] error while jinja_native rendering value, error was: " + str(error))
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
                value_for_json = value = self.jinja_render_value( template = jinja_expr, context = context )

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

  def filters(self):
    return {
      'jtable': ansible_filter
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
        for item in dataset:
            for key,value in item.items():
                self.cover_paths(value,[str(index),key])
                index+=1
            self.raw_rows = self.raw_rows + [ item ]

        return self.fields


class path_splitter:

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
    


if __name__ == '__main__':
    jtable_cli().parse_args()