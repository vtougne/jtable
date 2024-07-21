#!/usr/bin/env python3

class my_cls(object):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return {'name': self.name}


result = my_cls('vincent')

print(repr(result))

if __name__ == '__main__':
    import sys
    print('coucou')
