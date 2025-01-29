#!/usr/bin/env python3

from jinja2 import nativetypes, StrictUndefined
from yaml import load, Loader

class UnicodeString():
    def __init__(self, value):
        self.value = value
    
    def __str__(self):
        return self.value

    def __repr__(self):
        return f"UnicodeString({repr(self.value)})"

    def __add__(self, other):
        if isinstance(other, (str, UnicodeString)):
            # if "other" is an UnicodeString
            return UnicodeString(self.value + str(other))
        raise TypeError(f"Unsupported operand type(s) for +: 'UnicodeString' and '{type(other).__name__}'")

    def __radd__(self, other):
        # if "other" is a string
        if isinstance(other, str):
            return UnicodeString(other + self.value)
        raise TypeError(f"Unsupported operand type(s) for +: '{type(other).__name__}' and 'UnicodeString'")
    

class MyEnvironment(nativetypes.NativeEnvironment):
    pass

def cover_vars(data):
    vars = {}
    env = MyEnvironment()
    for key, value in data["vars"].items():
        print(f"debug key: {key} / value: {value}") 
        # evalued_value = parse_var(value,vars)
        str_object = value
        template = env.from_string(str_object)
        evalued_value =  template.render(vars)
        print(f"debug value type: {type(value)} / evalued_value: {type(evalued_value)}")
        vars.update({key: evalued_value})
    return vars





if __name__ == "__main__":
    env = MyEnvironment()
    template = env.from_string("{{ value  }}")

    the_string = "['vince']"
    value=UnicodeString(the_string)
    # value=the_string

    try:
        output = template.render(value=value)
    except Exception as error:
        print(error)
        print(dir(error))
        print(error.__str__)
        exit(2)
        
    print(output)
    print(type(output))
    data = {"vars": {"name": "['vince']"}}
    vars = cover_vars(data)
    print(vars)
    print(type(vars))