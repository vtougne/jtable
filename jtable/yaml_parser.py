#!/usr/bin/env python3
from yaml import load, Loader
from jinja2 import nativetypes, StrictUndefined
from templater import Templater
from logger import CustomFormatter, CustomFilter, _ExcludeErrorsFilter, logging_config
import logging, logging.config
import sys



class UnicodeString:
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


def cover_vars(data):
    vars = {}
    # env = MyEnvironment()
    for key, value in data["vars"].items():
        logging.info(f"key: {key} / value: {value}") 
        evalued_value = parse_var(value,vars)
        logging.info(f"value type: {type(value)} / evalued_value: {type(evalued_value)}")
        vars.update({key: evalued_value})
    return vars

def load_yaml(file_path):
    with open(file_path, 'r') as file:
        return load(file, Loader=Loader)


def parse_var(var,context):
    logging.info(f"var: {var}, type: {type(var)} context: {context}")
    
    if isinstance(var, str) or isinstance(var, int):
        # str_object = UnicodeString(var)
        str_object = str(var)
        templated_object =  Templater(str_object).render(context)
        logging.info(f"type templated_object: {type(templated_object)}")
        return templated_object
    elif isinstance(var, list):
        return [parse_var(v,context) for v in var]
    elif isinstance(var, dict):
        return {k: parse_var(v,context) for k, v in var.items()}
    else:
        logging.error(f"Unsupported type for var: {type(var)}")
        exit(3)


if __name__ == '__main__':

    logging_config['handlers']['console_stderr']['level'] = 'DEBUG'
    logging_config['formatters']['my_formatter']['format'] = '%(asctime)s (%(lineno)s) %(class_name)s.%(parent_function)-16s | %(levelname)s %(message)s'
    logging.config.dictConfig(logging_config)

    
    yaml_file = sys.argv[1]
    query_data = load_yaml(yaml_file)
    print(cover_vars(query_data))
    
    # the_dict = [{"name": "John", "age": 30}, {"name": "Jane", "age": 25}, {"name": "Doe", "age": 35}]
    # print(parse_var(the_dict,{}))