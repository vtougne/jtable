#!/usr/bin/env python3

import yaml, sys
# from jinja2 import Environment, BaseLoader
from tabulate import tabulate

from ansible.template import Templar,AnsibleContext,AnsibleEnvironment
from ansible.parsing.dataloader import DataLoader


import argparse
parser = argparse.ArgumentParser(description='ansible templater')
parser.add_argument("-t", "--template", help = "template to apply")
parser.add_argument("-d", "--dataset", help = "dataset")
args = parser.parse_args()


if len(sys.argv)<2:
    parser.print_help()
    exit(1)

if args.template:
    template_file_name = args.template
else:
    print('Error template arg is mandatory')
    parser.print_help
    exit(1)
    
if args.dataset:
    dataset_file_name = args.dataset
else:
    print('Error dataset arg is mandatory')
    parser.print_help
    exit(1)


with open(dataset_file_name, 'r') as dataset_file:
    dataset = yaml.safe_load(dataset_file)
        
    
template = open(template_file_name, 'r').read()


loader = DataLoader()
templar = Templar(loader=loader,variables = dataset )
table_object = templar.template(template)
print(table_object['text'])

