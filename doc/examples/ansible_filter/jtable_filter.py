#!/usr/bin/env python3
import os, sys

from ansible.module_utils.basic import AnsibleModule


# from data_cls import data_cls
import site
print(site.getusersitepackages())

def jtable_filter(dataset,select=[],path="stdin{}",format="text"):
    from jtable import jtable
    print(jtable.__file__)
    return jtable.JtableCls(render="jinja_ansible").render_object({"stdin": dataset},path=path, select=select)[format]

class FilterModule(object):

  def filters(self):
    return {
      'jtable': jtable_filter
    }
