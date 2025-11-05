# import to_table
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
        'wordcount', 'wordwrap', 'xmlattr', 'tojson', 'items', 'keys',
        'values'
    ]
class to_table:
    pass
class to_yaml:
    pass

class AppsModule(object):

  def apps(self):
    return {
      'to_table': { "app": to_table, "types": ["filter"] },
      'to_yaml':  { "app": to_yaml , "types": ["filter"] },
      }
  
  def list_apps(self):
    return list(self.apps().keys())
  
  def list_builtins(self):
    return jinja_builtins
  
  def list_all(self):
    return sorted(jinja_builtins + list(self.apps().keys()))
