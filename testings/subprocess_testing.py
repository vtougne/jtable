#!/usr/bin/env python3

import subprocess
import shutil
import os, sys
import platform

script_to_submit = """
echo "Hello, world!"
echo "Current directory: $(pwd)"
jtable --version
./simu_infra_inv.py
"""


# export PYTHONPATH=${PWD}/jtable
import functions

context = functions.running_context()
shell_type = context["shell_type"]

if shell_type == "git_bash" or shell_type == "cygwin":
    bash_path = shutil.which("bash.exe")
else:
    bash_path = shutil.which("bash")

if bash_path is None:
    raise FileNotFoundError(f"bash_path {bash_path} was not found in PATH")
output = subprocess.run(
    [bash_path, "-c", script_to_submit],
    check=True,
    stdout=subprocess.PIPE,  # Capture stdout et stderr
    stderr=sys.stderr,
    text=True  # Retourne les résultats en tant que chaîne de caractères
)

print(f"Output: {output.stdout}")
