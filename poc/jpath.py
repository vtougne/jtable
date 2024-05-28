#!/usr/bin/python3
import yaml
from yaml.loader import SafeLoader
import sys,json
from tabulate import tabulate

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
      

stdin=""
for line in sys.stdin:
    stdin = stdin + line

my_data_cls = Inspect()

out = my_data_cls.view_paths(yaml.safe_load(stdin))
# print(out)

tbl = tabulate(out,['path','value'])
print(tbl)
# print('\n'.join(my_data_cls.out))

# print(the_path)