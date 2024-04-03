#!/usr/bin/env python3
import os, sys

from ansible.module_utils.basic import AnsibleModule


# from data_cls import data_cls
from jtable import jtable_cls

def jtable_filter(dataset,select=[]):
    data = jtable_cls()

    return data.to_table(dataset,path="",select=select)
    # return tabulate(data.rows)
    # return os.environ 

class FilterModule(object):

  def filters(self):
    return {
      'jtable': jtable_filter
      
    }
