#!/usr/bin/env python3
import sys,os

parent_path = '/'.join(__file__.split("/")[:-4]) + "/jtable"
sys.path.append(parent_path)

try:
   import jtable.jtable as jtable
except:
   import jtable
  
# print(dir(jtable))

def jtable_filter(dataset,select=[],path="{}",format="simple",views={}, when=[],queryset={}):
    return jtable.JtableCls(render="jinja_ansible").render_object( dataset,path=path, select=select,views=views, when=when,format=format, queryset=queryset)

def wrap_html(body):
    # print('coucou')
    return jtable.Filters.wrap_html(body)

class FilterModule(object):

  def filters(self):
    return {
      'jtable': jtable_filter,
      'wrap_html': wrap_html
    }
  