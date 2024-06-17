#!/usr/bin/env python3
import os, sys

from ansible.module_utils.basic import AnsibleModule
# sys.path.append('.')
# current_dir = os.path.dirname(__file__)
# root_path = os.path.abspath(os.path.join(current_dir, '..'))
# sys.path.append(root_path)
# print('coucou from jtable_filter')

# from data_cls import data_cls
# from jtable import jtable_cls

def my_filter(dataset,select=[]):
    return sys.path

class FilterModule(object):

  def filters(self):
    return {
      'my_filter': my_filter
      
    }
