#!/usr/bin/env python3
import inspect
import os
import sys

current_path = os.path.dirname(os.path.abspath(__file__))
parent_path = os.path.dirname(current_path)
if parent_path not in sys.path:
    sys.path.insert(0, parent_path)

def my_func( the_str="",the_dict={}):
    pass

import to_table
import functions
from jinja2 import Environment, StrictUndefined, Undefined
import jinja2
env = Environment

# for member in inspect.getmembers(my_func):
#     print(f"{member[0]}: {member[1]}")
#     for prop in dir(member[1]):
#         if not prop.startswith("__"):
#             print(f"    {prop}: {getattr(member[1], prop)}")
    

# targeted_fun = to_table.ToTable.render_object
# targeted_fun = my_func

# print(dir(jinja2.filters))

# print(jinja2.filters.FILTERS)

# print(jinja2.filters.FILTERS['replace']())
# print(inspect.getmembers(jinja2.filters.FILTERS['replace']))
# exit(0)

# for filter in jinja2.filters.FILTERS.items():
#     print(f"{filter[0]}")
#     for prop in dir(filter[1]):
#         if not prop.startswith("__"):
#             print(f"    {prop}: {getattr(filter[1], prop)}")



# # print(inspect.getmembers(env))

# for member in inspect.getmembers(jinja2.filters.FILTERS):
#     print(f"{member[0]}: {member[1]}")
#     for prop in dir(member[1]):
#         if not prop.startswith("__"):
#             print(f"    {prop}: {getattr(member[1], prop)}")


targeted_fun= jinja2.filters.FILTERS['replace']

# print(targeted_fun.__code__.co_varnames)
# print(targeted_fun.__doc__)
# for prop in dir(targeted_fun.__code__):
#     if not prop.startswith("__"):
#         print(f"    {prop}: {getattr(targeted_fun.__code__, prop)}")

for func in jinja2.filters.FILTERS.items():
    print(f"Function {func[0]}:")
    for prop in dir(func):
        if prop == "__doc__":
            print(f"    {func[1].__doc__}")
    print(f"Available properties for function {func[0]}:")
    for prop in dir(func[1]):
        if prop == "__code__":
            print(f"    {func[1].__code__.co_varnames}")
    print("")
    print("                 =============================                 ")
    print("")

# for prop in dir(targeted_fun):
#     if "__doc__" in prop:
#         print(f"    {prop}: {getattr(targeted_fun, prop)}")
#     if "__code__" in prop:
#         if "co_varnames" in dir(getattr(targeted_fun, prop)):
#             print(f"    {prop}.co_varnames: {getattr(targeted_fun.__code__, 'co_varnames')}")