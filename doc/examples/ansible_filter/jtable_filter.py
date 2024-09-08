#!/usr/bin/env python3
import os, sys

from ansible.module_utils.basic import AnsibleModule


# from data_cls import data_cls
import site
print(site.getusersitepackages())

def jtable_filter(dataset,select=[],path="{}",format="simple",views={}, when=[],queryset={}):
    from jtable import jtable
    # print(jtable.__file__)
    # print(dataset)
    # return jtable.JtableCls(render="jinja_ansible").render_object({"stdin": dataset},path=path, select=select)[format]
    return jtable.JtableCls(render="jinja_ansible").render_object( dataset,path=path, select=select,views=views, when=when,format=format, queryset=queryset)

class FilterModule(object):

  def filters(self):
    return {
      'jtable': jtable_filter
    }
