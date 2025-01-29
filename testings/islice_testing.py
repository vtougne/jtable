#!/usr/bin/env python3

from itertools import islice


li = [2, 4, 5, 7, 8, 10, 20]

print(list(islice(li, 1, 6, 2)))
