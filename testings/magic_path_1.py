#!/usr/bin/env python3
import re, sys

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


path = "planet.jack['data_center'}][{ds}]{elton}.simon['roger']['bob'].bo"
if len(sys.argv)>1:
    path = sys.argv[1]

# my_pagic_path = path_splitter()

# path_list = my_pagic_path.crunch_path(magic_path)
# print(path_list)

splitted_path = path_splitter().crunch_path(path)

print('\n'.join(splitted_path))
