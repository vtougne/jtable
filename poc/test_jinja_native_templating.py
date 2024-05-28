#!/usr/bin/env python3
from jinja2 import Environment, BaseLoader


str_to_template = "salut {{ regions[0].dc_1 }}"
context = { "regions": [{ "dc_1": "max"}]}
# context = { "name": "vince "}

# loader = BaseLoader().from_string(myString)


# mplate = Environment(loader=loader)
loader=BaseLoader()
tenv = Environment(loader=loader)
mplate =tenv.from_string(str_to_template)
out = mplate.render(**context)

print(out)