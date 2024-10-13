#!/usr/bin/env python3

class my_cls(object):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"Hello {self.name}"


result = my_cls('Vince')

print(result)
