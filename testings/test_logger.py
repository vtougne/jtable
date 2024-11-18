#!/usr/bin/env python3

from logger_cls import hello

# print(hello())


class ClassOne :
    def hello(self):
        return "Hello, from ClassOne!"
    
class ClassTwo :
    def hello(self):
        return "Hello, from ClassTwo!"

if __name__ == '__main__':
    obj1 = ClassOne()
    obj2 = ClassTwo()
    print(obj1.hello())
    print(obj2.hello())