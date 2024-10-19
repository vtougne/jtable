#!/usr/bin/env python3
import sys,os

# print(sys.path)
# parent_path = (os.path.realpath("f{__file__}/.."))
# print(parent_path)
# parent_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
parent_path = '/'.join(__file__.split("/")[:-4]) + "/jtable"
# parent_path = '/'.join(__file__.split("/")[:-2])
# print(parent_path)
# exit(0)
sys.path.append(parent_path)

try:
   import jtable
except:
  import jtable.jtable as jtable
# print(dir(jtable))

def jtable_filter(dataset,select=[],path="{}",format="simple",views={}, when=[],queryset={}):
    # print(jtable.__file__)
    # print(dataset)
    # return jtable.JtableCls(render="jinja_ansible").render_object({"stdin": dataset},path=path, select=select)[format]
    return jtable.JtableCls(render="jinja_ansible").render_object( dataset,path=path, select=select,views=views, when=when,format=format, queryset=queryset)

class FilterModule(object):

  def filters(self):
    return {
      'jtable': jtable_filter
    }