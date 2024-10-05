import yaml, sys
# from jinja2 import Environment, BaseLoader



class data_cls:
    def __init__(self):
        self.path = "...Undefined"
        self.paths = []
        self.fields = []
        self.rows = []
        self.raw_rows = []
        self.source_object_type = "list"

    def get_paths(self,dataset):
        self.cover_paths(dataset)
        return('\n'.join(self.paths))
    
    def cover_paths(self,dataset,path=[]):
        if type(dataset) is dict:
            for key,value in dataset.items():
                the_path = path + [ key ]
                self.cover_paths(value,the_path )
        elif type(dataset) is list:
            pass
            # index=0
            # for item in dataset:
            #     index += 1
            #     the_path = path + [ str(index) ]
            #     self.cover_paths(item,the_path)
        else:
            self.paths = self.paths + [ path + [dataset] ]
            if path[1:] not in self.fields:
                self.fields = self.fields + [path[1:]]

    def cover_data(self,dataset):
        
        if type(dataset) is dict:
            the_list = []
            for key,value in dataset.items():
                the_list = the_list + [ {'key': key, 'value': value} ]
                self.source_object_type="dict"
            self.cover_data(the_list)
        elif type(dataset) is list:
            index=0
            for item in dataset:
                for key,value in item.items():
                    self.cover_paths(value,[str(index),key])
                    index+=1
                self.raw_rows = self.raw_rows + [ item ]

    def to_table(self,dataset,path=""):
      if path != self.path:
        self.__init__()
        self.path = path
        dataset = eval('dataset' + path )
        self.cover_data(dataset)
        for item in self.raw_rows:
            row=[]
            for field in self.fields:
                try:
                    cell=eval('item[\'' + '\'][\''.join(field) + '\']')
                except:
                    cell=""
                row = row + [ cell ]
            #   print(row)
            self.rows = self.rows + [ row ]

    def load_data(self):
        stdin=""
        for line in sys.stdin:
            stdin = stdin + line
        input = yaml.safe_load(stdin)
        return(input)
    
    def path_explorer_view():
        pass 

    def select_view(self):
        return('\n'.join(str(field) for field in self.fields))
    