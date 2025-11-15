#!/usr/bin/env python3
# import to_tablev
# from functions import *

import os
import sys
import inspect

current_path = os.path.dirname(os.path.abspath(__file__))
parent_path = os.path.dirname(current_path)
if parent_path not in sys.path:
    sys.path.insert(0, parent_path)

import functions


jinja_builtins = [
        'abs', 'attr', 'batch', 'capitalize', 'center', 'default',
        'dictsort', 'escape', 'filesizeformat', 'first', 'float',
        'forceescape', 'format', 'groupby', 'indent', 'int', 'join',
        'last', 'length', 'list', 'lower', 'map', 'max', 'min',
        'pprint', 'random', 'reject', 'rejectattr', 'replace',
        'reverse', 'round', 'safe', 'select', 'selectattr', 'slice',
        'sort', 'string', 'striptags', 'sum', 'title', 'trim',
        'truncate', 'unique', 'upper', 'urlencode', 'urlize',
        'wordcount', 'wordwrap', 'xmlattr', 'items', 'keys',
        'values'
    ]
def to_table():
    pass
def to_yaml():
    pass

class AppsModule(object):

  def apps(self):
    return {
      'to_table': { "app": to_table, "types": ["filter"] },
      'to_yaml':  { "app": to_yaml , "types": ["filter"] },
      'load_json':  { "app": to_yaml , "types": ["method"] },
      }
  
  def list_apps(self):
    return list(self.apps().keys())
  
  def list_builtins(self):
    return jinja_builtins
  
  def list_all(self):
    return sorted(jinja_builtins + list(self.apps().keys()))
  
  def list_filters(self):
    return [name for name, info in self.apps().items() if "filter" in info["types"]] + jinja_builtins
  
  def list_methods(self):
    return [name for name, info in self.apps().items() if "method" in info["types"]]
  
  def list_functions(self):
    # all_functions = [name[0] for name in inspect.getmembers(functions, predicate=inspect.isfunction)]


    for func in inspect.getmembers(functions, predicate=inspect.isfunction):
          print(f"*******           {func[0]}            ********")
          for prop in dir(func):
              print(f"      {prop}: {getattr(func, prop)}")
          print("")

    # return all_functions


if __name__ == "__main__":
    apps_module = AppsModule()
    # print("Available methods:")
    # print("\n".join(apps_module.list_methods()))
    # print(apps_module.list_functions())
    # inspect_wrap_html=inspect.getmembers(functions.wrap_html)
    # print(dir(inspect_wrap_html))
    


    for member in inspect.getmembers(functions.wrap_html):
        print(f"{member[0]}: {member[1]}")
        for prop in dir(member[1]):
            if not prop.startswith("__"):
              print(f"    {prop}: {getattr(member[1], prop)}")
        

