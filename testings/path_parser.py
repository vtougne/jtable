#!/usr/bin/env python3
import re, sys


jinja_path = "users[4]['the_name']['bob'][3]"

element_types = {
    "dict": {
        "start": "[",
        "end": "]",
        "quote": "'"
    },
    "list": {
        "start": "[",
        "end": "]",
        "quote": ""
    },
    "object": {
        "start": "{",
        "end": "}",
        "quote": ""
    }
}

modes = {
    "start_looking_for_element": {
        "accepeted_chars":
            ["[", "{", ".", "']"],
    }
}

class PathSplitter:
    def __init__(self):
        self.path_list = []
        self.mode = "start_looking_for_element"

    def parse_path(self,path):
        print(path)
        if self.mode == "start_looking_for_element":
            pass


# reversed_path = jinja_path[::-1]
# print(reversed_path)
PathSplitter().parse_path(jinja_path)