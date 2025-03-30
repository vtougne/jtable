#!/usr/bin/env python3

from jinja2 import Environment, meta

template_str = "{{ 'Hello' + users[4]['the_name'] + 'how are you?' }}"
template_str = "{{ users[4]['the_name']['{ bob }'][3] }}"
# template_str = "{{ 'Hello' + users[4]['the_\\'name'] + 'how are you?' }}"

env = Environment()
parsed_content = env.parse(template_str)
variables = meta.find_undeclared_variables(parsed_content)

def field_parser(fields):
    print(f"fields type: {type(fields)}")
    print(list(fields))
    for field in fields:
        print(f"field: {field}")
        print(f"field type: {type(field)}")

def cover_items(parserd_content):
    # print(dir(parserd_content))
    if hasattr(parserd_content, 'iter_child_nodes'):
        cover_items(parserd_content.iter_child_nodes())
    if hasattr(parserd_content, 'iter_fields'):
        print('iter_fields')
        for fields in parserd_content.iter_fields():
            # print(f"Field: {fields}")
            # for field in fields:
            #     print(f"field: {field}")
            #     print(f"field type: {type(field)}")
            field_parser(fields)

cover_items(parsed_content)