#!/usr/bin/env python3

import re
import sys

user_input = sys.argv[1]

if not user_input:
    s = r"[vince][dupont][status: \[not contacted\]]"
else:
    s = user_input

# 1.  On capture chaque bloc entre crochets, mais on accepte les crochets échappés à l’intérieur
pattern = r'\[(?:\\.|[^\]])*\]'

blocks = re.findall(pattern, s)

# print('\n'.join(blocks))  # ['[vince]', '[dupont]', '[status: \\[not contacted\\]]']

# 3.  On dé‑échappe les séquences \[ et \] (et d’autres éventuels caractères échappés)
blocks = [re.sub(r'\\([\\\[\]])', r'\1', b) for b in blocks]

# print(blocks)   # ['vince', 'dupont', 'status: [not contacted]']
print('\n'.join(blocks))  # ['[vince]', '[dupont]', '[status: \\[not contacted\\]]']
