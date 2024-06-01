#!/usr/bin/env python3
import re, sys, os
from os import listdir, system
import subprocess


path = "dataset.yml"

if len(sys.argv)>1:
    path = sys.argv[1]


files = os.popen("ls -1 " + path).read()

for file in files.split('\n'):
    if file != '':
        print('debug file: ' + file)

