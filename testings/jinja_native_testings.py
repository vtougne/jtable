#!/usr/bin/env python3

from jinja2 import nativetypes, StrictUndefined

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




if __name__ == "__main__":
    env = MyEnvironment()
    template_string = "['john','{{ value }}']"
    template = env.from_string(template_string)

    the_string = "vince"
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
