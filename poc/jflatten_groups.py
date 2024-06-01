#!/usr/bin/python3
import yaml
from yaml.loader import SafeLoader
import sys,json, ast

class data_cls:
    def __init__(self):
        self.out = []
        self.current_path = []
        
    def add_row(self,row):
        self.out = self.out + [ row ]
    
    def cover_data(self,dataset,current_path=[],path_level=0):
        # print('debug current_path ' + str(path_level) + ': ' + ''.join(current_path))
        current_position = current_path[0: path_level -1 ]
        print('debug current_position: ' + str(current_position))
        print('debug self.path_2_cross: ' + str(self.path_2_cross))
        # if str(current_position) == str(self.path_2_cross):
        #     print('youhouuuuuuuuuuuuuuuu')

        
        if type(dataset) is dict:
            for key,value in dataset.items():
                the_current_path = current_path + [ '[\'' + str(key) + '\']' ]
                the_path_level = path_level + 1
                self.cover_data(value,the_current_path,the_path_level)
        elif type(dataset) is list:
            index=0
            for item in dataset:
                index += 1
                the_current_path = current_path +  [ '[' + str(index) + ']' ]
                the_path_level = path_level + 1
                self.cover_data(item,the_current_path,the_path_level)
        else:
            my_data_cls.add_row(''.join(current_path) + ': ' + str(dataset))
        
    def get_path(self,dataset,path_2_cross):
        self.path_2_cross = path_2_cross
        self.cover_data(dataset)
        print('debug path_2_cross: ' + str(path_2_cross))
        return('\n'.join(self.out))

stdin=""
for line in sys.stdin:
    stdin = stdin + line
    
path_2_cross=(sys.argv[1])
dataset = yaml.safe_load(stdin)


my_data_cls = data_cls()

out = my_data_cls.get_path(dataset,path_2_cross)
# print(out)
