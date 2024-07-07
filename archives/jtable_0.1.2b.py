#!/usr/bin/env python3
import yaml, sys, json, re, os, ast
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
        parser.add_argument("-p", "--json_path", help = "Show Output")
        parser.add_argument("-f", "--format", help = "text,json,th,td")

        args = parser.parse_args()
        dataset = {}
        stdin=""
        for line in sys.stdin:
            stdin = stdin + line
        # dataset = yaml.safe_load(stdin)
        dataset = {**dataset, **{ path_var_name: yaml.safe_load(stdin) } }
    

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
    
    def cross_path(self,path_level=0):
        if path_level < len(self.path_splitted):
            self.cross_path(path_level + 1)
        else:
            current_path_splitted = self.path_splitted[0:path_level + 1]
            if current_path_splitted[-1][0] == "{":
                self.item_name = re.sub(r'^.(.*).$',r'\1',current_path_splitted[-1])
                
                template = '{{ ' + ''.join(self.path_splitted[0:path_level - 1]) + '}}'
                dataset = self.jinja_render_value( template = template, context = self.dataset )
                self.render_table(dataset,select=self.select,item_name = self.item_name)
                

    
    def render_table(self,dataset,select=[],item_name = ''):
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
                context = { item_name: item } if item_name != '' else item
                # print('debug context: ' + str(context))
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


    
    def render_object(self,dataset,path=path,select=[]):
        self.dataset = dataset
        self.select = select
        self.path_splitted =   path_splitter().split_path(path,"[{.")
        self.cross_path()
        # exit(0)

        # if path != "":
        #     template = '{{ ' + path + '}}'
        #     dataset = self.jinja_render_value( template = template, context = dataset )
        # self.render_table(dataset,select=select)
     
            
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
                elif self.item_name == "":
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
            the_list = []
            for key,value in dataset.items():
                the_list = the_list + [ {'key': key, 'value': value} ]
            self.discover_paths(the_list)
        # then call itself because dataset is sure a list
        elif type(dataset) is list:
            index=0
            for item in dataset:
                for key,value in item.items():
                    self.cover_paths(value,[str(index),key])
                    index+=1
                self.raw_rows = self.raw_rows + [ item ]

        return self.fields


class path_splitter:

    def cover_path(self,path=path,surround_str=""):
        if len(path) > 0:
            left_part = (re.sub(r'^(.[^' + surround_str + ']*).*',r'\1',path))
            remaining_path = path[len(left_part):]
            if len(left_part) > 0:
                self.path_list = self.path_list +  [left_part]
                self.cover_path(remaining_path, surround_str)
                
    def extract_var_from_path(self,path):
        if len(path) > 0:
            left_part = re.sub(r'^([^[^\.^{]*).*',r'\1',path)
            self.path_list = [left_part]
            remaining_path = path[len(left_part):]
            return remaining_path
    
    def split_path(self,path=path,surround_str=""):
        remaining_path = self.extract_var_from_path(path)
        self.cover_path(remaining_path, surround_str)
        return self.path_list
    

if __name__ == '__main__':
    jtable_cli().parse_args()