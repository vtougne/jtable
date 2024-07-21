#!/usr/bin/env python3

class my_cls(object):

    def hello(self, name):
        print(sys.argv)
        return "Heelo " + name


if __name__ == '__main__':
    import sys
    print(my_cls().hello("vince"))
