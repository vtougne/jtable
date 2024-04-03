import yaml, sys, json
# from jinja2 import Environment, BaseLoader
from tabulate import tabulate

from ansible.template import Templar,AnsibleContext,AnsibleEnvironment
from ansible.parsing.dataloader import DataLoader

default_outs = "json,text"
loader = DataLoader()

class jtable_cls:
    def __init__(self):
        self.path = "...Undefined"
        self.paths = []
        self.fields = []
        self.td = []
        self.th = []
        self.raw_rows = []
        self.source_object_type = "list"
        self.table_headers = []
        self.json = []


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
        # self.table_headers = list(map(lambda item: '.'.join(item), self.fields))

    def cover_data(self,dataset):
        
        # when input is dict transform as list like dict2items
        if type(dataset) is dict:
            the_list = []
            for key,value in dataset.items():
                the_list = the_list + [ {'key': key, 'value': value} ]
                self.source_object_type="dict"
            self.cover_data(the_list)
        # then call itself because dataset is sure a list
        elif type(dataset) is list:
            index=0
            for item in dataset:
                for key,value in item.items():
                    self.cover_paths(value,[str(index),key])
                    index+=1
                self.raw_rows = self.raw_rows + [ item ]

    
    def get_paths(self,dataset):
        self.cover_paths(dataset)
        return('\n'.join(self.paths))
    

    def to_table(self,dataset,path="",select=[], out=default_outs):
        self.path = path

        templar = Templar(loader=loader,variables = dataset)
        if path != "":
            dataset = templar.template('{{ ' + path + '}}')
        
        if type(dataset) is dict:
            dataset_to_cover = []
            for key,value in dataset.items():
                dataset_to_cover = dataset_to_cover + [ {'key': key, 'value': value} ]
        elif type(dataset) is list:
            dataset_to_cover = dataset
        else:
            print('error dataset must be a dict or list, was: ' + type(dataset))
            return 1
        
        fields_label = None
        
        
        if len(select) > 0:
            expressions = [expressions['expr'] for expressions in select]
            fields_label = [fields_label['as'] for fields_label in select]
        else:
            self.cover_data(dataset)
            fields_label = list(map(lambda item: '.'.join(item), self.fields))
            expressions = list(map(lambda item:  'item[\'' + '\'][\''.join(item) + '\']' , self.fields))
            
            dataset_to_cover = self.raw_rows

        
            
        for item in dataset_to_cover:
            row = []
            json_dict = {}
            row_index = 0
            for expr in expressions:
                try:
                    context=item
                    jinja_expr = '{{ ' + expr  + '| default(None)' + ' }}'
                    templar = Templar(loader=loader, variables={'item': context})
                    value = templar.template(jinja_expr)
                    
                except Exception as error:
                    # print('debug jinja_expr: ' + jinja_expr)
                    value = error
                
                key = fields_label[row_index]
                json_value = { key: value } if "json" in out.split(',')  else None
                # print('debug json_value: ' + str(json_value))
                    
                row = row + [ value ]
                json_dict = {**json_dict, **json_value }
                value = None
                row_index += 1
            
            self.td = self.td + [ row ]
            self.json = self.json + [ json_dict ]
                
        
        if fields_label is None:
            headers = list(map(lambda item: '.'.join(item), expressions))
            fields_label = headers
        
        self.th = fields_label
            
        # print('debug ' + str(fields_label))
        # print(self.th)
        # print(self.td)
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
            "json": json.dumps(self.json)
        }
            
        # return tabulate(self.td,self.th)
        return out_return

    def load_data(self):
        stdin=""
        for line in sys.stdin:
            stdin = stdin + line
        input = yaml.safe_load(stdin)
        return(input)
