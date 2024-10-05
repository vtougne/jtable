#!/usr/bin/env python3
import re, sys

class path_splitter:

    def cover_path(self,path="",surround_str=""):
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
    
    def split_path(self,path="",surround_str=""):
        remaining_path = self.extract_var_from_path(path)
        self.cover_path(remaining_path, surround_str)
        return self.path_list
        


path = "planet.jack['data_center'].elton.simon['roger']['bob'].bo"
if len(sys.argv)>1:
    path = sys.argv[1]


start_str = "[{."
print('path was: ' + path)
path_splitted =   path_splitter().split_path(path,start_str)
print('\n'.join(path_splitted))

# new_path_path_splitted = []
# for path in path_splitted[0:]:
#     new_path_path_splitted = new_path_path_splitted +  path_splitter().split_path(path,"]")

# print(new_path_path_splitted)



# print(re.sub(r'^(.*).*',r'\1',path))
# print(re.sub(r'^([^[]*).*',r'\1',path))

