#!/usr/bin/env python3
# import to_tablev
# from functions import *


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


if __name__ == "__main__":
    apps_module = AppsModule()
    print("Available methods:")
    print("\n".join(apps_module.list_methods()))