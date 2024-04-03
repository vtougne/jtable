#!/usr/bin/env python3
import os, sys, yaml

# from data_cls import data_cls
from jtable import jtable_cls
from tabulate import tabulate
import argparse
# from ansible.template import Templar,AnsibleContext,AnsibleEnvironment

select = []
expr = []
format="text"
parser = argparse.ArgumentParser(description='Tabulate your json data and render them using jinja')

# parser.add_argument("-s", "--select", help = "{ user.firstname as firstname, user.lastname as lastname}")
parser.add_argument("-q", "--query_file", help = "Show Output")
parser.add_argument("-p", "--json_path", help = "Show Output")
parser.add_argument("-f", "--format", help = "text,json,th,td")

args = parser.parse_args()

data = jtable_cls()
raw_data = data.load_data()
path = ""

if args.json_path:
    path = args.json_path
if args.format:
    format = args.format
if args.query_file:
    
    with open(args.query_file, 'r') as file:
        query_set = yaml.safe_load(file)
        # print('debug query_set: ' + str(query_set))
        if 'select' in query_set:
            select = query_set['select']
            print(data.to_table(raw_data,path=path,select=select)[format])
            
if (select == []):
    print(data.to_table(raw_data,path=path)[format])
            


