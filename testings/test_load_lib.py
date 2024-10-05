#!/usr/bin/env python3
import sys

print(sys.argv[1])

the_lib = sys.argv[1]
if the_lib == "bob":
    import re
elif the_lib == "jack":
    import yaml


print(yaml)