#!/usr/bin/env python3

from jinja2 import nativetypes, StrictUndefined
import inspect
import logging
import functions

class MyEnvironment(nativetypes.NativeEnvironment):
    pass

class Plugin:
    pass

class Filters():
    pass

class Templater:
    filter_names = [f[0] for f in inspect.getmembers(functions, inspect.isfunction)]
    def __init__(self, template_string = "", static_context = {},strict_undefined = True):
        self.strict_undefined = strict_undefined
        env  = MyEnvironment(undefined=StrictUndefined)
        import random
        self.id = random.randint(0,1000000)
        logging.info(f"filers: {self.filter_names}")

        
        logging.info(f"({self.id}) compiling template_string: {template_string}")
        logging.info(f"({self.id}) template_string type  {type(template_string)}")
        try:
            self.template = env.from_string(template_string, globals=static_context)
        except Exception as error:
            logging.error(f"({self.id}) Failed to compile template, error was:\n  {str(error)}")
            exit(3)
    
    def render(self, vars, eval_str = False):

        logging.debug(f"({self.id}) Rendering template, self.strict_undefined: {self.strict_undefined}, vars: {vars}")
        
        try:
            out = self.template.render(vars)
            logging.debug(f"({self.id}) type_out: {type(out)}, out: {out}")
        except Exception as error:
                logging.error(f"Failed while rendering context, error was:\n  {str(error)}")
                exit(3)
        return out


if __name__ == "__main__":
    import sys,inspect
    print(dir(functions))
    print(inspect.getmembers(functions, inspect.isfunction))
    f_list  = [f[0] for f in inspect.getmembers(functions, inspect.isfunction)]
    print(f_list)