#!/usr/bin/env python3
from mergedeep import merge

dict1 = {'users': { 'vince': 'toutouche'} }
dict2 = {'users': { 'max': 'foufou'} }
dict3 = {'users': { 'vince': 'rere'} }
         
# dict1 =  { 'vince': 'toutouche'}
# dict2 = { 'max': 'foufou'}
         
res = merge({}, dict1, dict2, dict3) 

print(res)