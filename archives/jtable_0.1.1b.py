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

default_outs = "json,text"
# loader = DataLoader()


def ansible_filter(dataset,select=[]):
    return jtable_cls().render_object(dataset,path="",select=select)


class jtable_cli:
    def parse_args(self):
        # import os, sys, yaml
        if 'JTABLE_RENDER' in os.environ:
            render=os.environ['JTABLE_RENDER']
        else:
            render="jinja_native"


        # from jtable import jtable_cls
        import argparse

        select = []
        format="text"
        path = ""
        parser = argparse.ArgumentParser(description='Tabulate your json data and render them using jinja')

        # parser.add_argument("-s", "--select", help = "{ user.firstname as firstname, user.lastname as lastname}")
        parser.add_argument("-q", "--query_file", help = "Show Output")
        parser.add_argument("-p", "--json_path", help = "Show Output")
        parser.add_argument("-f", "--format", help = "text,json,th,td")

        args = parser.parse_args()
        stdin=""
        for line in sys.stdin:
            stdin = stdin + line
        dataset = yaml.safe_load(stdin)
    

        if args.json_path:
            path = args.json_path
            
        if args.format:
            format = args.format
        
        if args.query_file:
            with open(args.query_file, 'r') as file:
                query_set = yaml.safe_load(file)
                if 'select' in query_set:
                    select = query_set['select']
                    

        print(jtable_cls(render=render).render_object(dataset,path=path,select=select)[format])





class jtable_cls:
    def __init__(self, render):
        self.td = []
        self.th = []
        self.table_headers = []
        self.json = []
        self.render = render

        if self.render == "jinja_ansible":
            self.loader = DataLoader()
        else:
            self.loader=BaseLoader()


    
    def render_object(self,dataset,path="",select=[], out=default_outs):
        if path != "":
            self.splitted_path = (path_splitter().crunch_path(path))
        
        # templar = Templar(loader=self.loader,variables = dataset)
        if path != "":
            # dataset = templar.template('{{ ' + path + '}}')
            template = '{{ ' + path + '}}'
            dataset = self.render_template( template = template, context = dataset )
        
        
        fields_label = None
        
        
        if len(select) > 0:
            expressions = [expressions['expr'] for expressions in select]
            fields_label = [fields_label['as'] for fields_label in select]
        else:
            # self.discover_paths(dataset)
            fields = path_explorer().discover_paths(dataset)

            fields_label = list(map(lambda item: '.'.join(item), fields))
            expressions = list(map(lambda item:  'item[\'' + '\'][\''.join(item) + '\']' , fields))
            
            # dataset_to_cover = self.raw_rows

        
        if type(dataset) is dict:
            dataset_to_cover = []
            for key,value in dataset.items():
                dataset_to_cover = dataset_to_cover + [ {'key': key, 'value': value} ]
        elif type(dataset) is list:
            dataset_to_cover = dataset
        else:
            print('[ERROR] dataset must be a dict or list, was: ' + str(type(dataset)))
            print(dataset)
            exit(2)
            
        for item in dataset_to_cover:
            row = []
            json_dict = {}
            row_index = 0
            for expr in expressions:
                jinja_expr = '{{ ' + expr  + ' }}'
                value_for_json = value = self.render_template( template = jinja_expr, context = { 'item': item } )

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
            json_content = json.dumps(self.json)
        except Exception as error:

            print(tabulate(self.td,self.th))
            # return(str(error))
            print('')
            print("ERROR!!  sometinh wrong with json rendering, tabme maight contains the error ")
            print('Errors was:')
            print(error)
            exit(2)
            
            
        out_return = {
            "th": self.th,
            "td": self.td,
            "text": tabulate(self.td,self.th),
            "json": json_content
        }
            
        # return tabulate(self.td,self.th)
        return out_return
    
    def render_template(self,template,context):
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
                    print("error while rendering value, error was: " + str(error))
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
                    print("error while rendering value, error was: " + str(error))
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



class path_explorer:
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
    def __init__(self):
        self.opened_bracketed_paths = []
        self.closed_bracketed_paths = []
        self.dotted_paths = []

    def crunch_path(self,path):
        opened_bracketed_paths = self.crunch_opened_braket_paths(path)
        for opened_bracketed_path in opened_bracketed_paths:
          self.crunch_closed_braket_paths(opened_bracketed_path)
        return self.closed_bracketed_paths

    def crunch_opened_braket_paths(self,path):
        left_open_braket_part=re.sub(r'([^\[]]*)\[.*', r'\1', path)
        if left_open_braket_part != "":
            self.opened_bracketed_paths = self.opened_bracketed_paths + [ left_open_braket_part ]
            remaining_path = path[len(left_open_braket_part):]
            self.crunch_opened_braket_paths(remaining_path)
        return self.opened_bracketed_paths
    
    def crunch_closed_braket_paths(self,path):
        first_char = path[0]
        if first_char == "[":
            left_closed_braket_part=re.sub(r'([^\]]*\]).*', r'\1', path)
            self.closed_bracketed_paths = self.closed_bracketed_paths + [ left_closed_braket_part ]
            
            remaining_path = path[len(left_closed_braket_part):]
            if remaining_path != "":
                self.crunch_closed_braket_paths(remaining_path)
        else:
            for splitted_path in path.split('.') :
                if splitted_path != "":
                    surrounded_key = "['"+ splitted_path + "']"
                    self.closed_bracketed_paths = self.closed_bracketed_paths + [ surrounded_key ]
                    

if __name__ == '__main__':
    jtable_cli().parse_args()