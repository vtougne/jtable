#!/usr/bin/env python3
import os, sys

from ansible.module_utils.basic import AnsibleModule


# from data_cls import data_cls
def jtable_filter(dataset,select=[],path="stdin{}",format="text"):
    from jtable.cli import JtableCls
    return JtableCls(render="jinja_ansible").render_object({"stdin": dataset},path=path, select=select)[format]

class FilterModule(object):

  def filters(self):
    return {
      'jtable': jtable_filter
    }
