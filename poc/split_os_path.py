#!/usr/bin/env python3
import re, sys, os
from os import listdir, system
import subprocess
import yaml, sys, json, re, os, ast
import itertools



path = "dataset.yml"

if len(sys.argv)>1:
    path = sys.argv[1]


# files = os.popen("ls -1 " + path).read()

# for file in files.split('\n'):
#     if file != '':
#         print('debug file: ' + file)

class multifile_loader:
    def __init__(self):
        self.path_mask_str = ""
        self.files = []
        self.dataset = {}
        
    def build_dict(self,path):
        splitted_path = path.split('/')
        if len(splitted_path) > 1:
            current_stage = splitted_path[0]
            remaing_path = '/'.join(splitted_path[1:])
            print('debug remaing_path: ' + remaing_path)
            if current_stage in self.dataset:
                print('coucou')
            else:
                self.dataset = { **self.dataset, **{ current_stage: None }}
            self.build_dict(remaing_path)
        
    
    def list_files(self, path_str=""):
        files_str = os.popen("ls -1 " + path_str).read()
        for file_name in files_str.split('\n'):
            if file_name != '':
                self.files = self.files  + [file_name]
        return self.files
    
    def load_files(self, path_str=""):
        file_list = multifile_loader().list_files(path_str)
        # list_0 =  list(map(lambda stage: stage.split('/')[1]  , file_list))
        # print([k for k,v in (itertools.groupby(list_0))])
        for file_name in file_list:
            self.build_dict(file_name)
        
        return self.dataset
        


file_list = multifile_loader().load_files(path)
print('\n'.join(file_list))
