#!/usr/bin/env python3

import yaml, sys
# from jinja2 import Environment, BaseLoader
from tabulate import tabulate

from ansible.template import Templar,AnsibleContext,AnsibleEnvironment
from ansible.parsing.dataloader import DataLoader


import argparse
parser = argparse.ArgumentParser(description='ansible templater')


str_to_template = "{{ regions[0].dc_1 }}"
context = { "regions": [{ "dc_1": "youhou"}]}


loader = DataLoader()
templar = Templar(loader=loader,variables = context )
out = templar.template(str_to_template)
print(out)
print(dir(templar))
print(dir(templar.template))
print(templar.template.__str__)

# stdin=""
# for line in sys.stdin:
#     stdin = stdin + line

# print(stdin)
# input = yaml.safe_load(stdin)
# return(input)

# loader = DataLoader()
# templar = Templar(loader=loader,variables = {} )
# dataset = templar.template(stdin)

# print(dataset)

# print()
