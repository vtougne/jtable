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