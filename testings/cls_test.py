#!/usr/bin/env python3

class my_cls(object):
    def __init__(self, name):
        print(f"initializing my_cls with name: {name}")
        self.name = name

    def __repr__(self):
        return f"repr {self.name}"
    
class my_cls_2(object):
    name = "my_cls_2_jhon"
    def __init__(self, name):
        print(f"initializing my_cls_2 with name: {name}")
        self.name = name
    def coucou(self):
        return f"coucou {my_cls_2.name}"



class the_cls(my_cls_2,my_cls):
  pass

result = the_cls('Vince').coucou()

print(result)
