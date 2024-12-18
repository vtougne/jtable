#!/usr/bin/env python3

print('start')

import sys
from os import isatty


is_pipe = not isatty(sys.stdin.fileno())

print(f"debug: sys.stdin: {sys.stdin}")
print(f"debug: is_pipe: {is_pipe}")


stdin=""
if is_pipe:
    print("stdin is a pipe")
    for line in sys.stdin:
        stdin = stdin + line
else:
    print('no pipe')

print(stdin)