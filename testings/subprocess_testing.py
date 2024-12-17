#!/usr/bin/env python3

import subprocess
import shutil
import os
import platform

script = """
#! /bin/bash
echo "Hello, world!"
echo "Current directory: $(pwd)"
"""


# export PYTHONPATH=${PWD}/jtable
import functions

print(functions.running_os())

bash_path = shutil.which("bash.exe")
if bash_path is None:
    raise FileNotFoundError("bash.exe introuvable. Vérifiez que Git Bash est installé et dans le PATH.")

# output = subprocess.run([bash_path, "-c", script], check=True)

output = subprocess.run(
    [bash_path, "-c", script],
    check=True,
    capture_output=True,  # Capture stdout et stderr
    text=True  # Retourne les résultats en tant que chaîne de caractères
)



exit(0)

running_platform = platform.system()

if running_platform == "Windows":
    if ms_system == "MINGW64" or ms_system == "CLANGARM64":
        running_os = "Linux"
    elif os.environ.get('TERM', '')  == "xterm":
            running_os = "Linux"
    else:
        running_os = "Windows"
else:
    running_os = running_platform


ms_system = os.environ.get('MSYSTEM', '')

print(f"info - MSYSTEM: {ms_system}")





# Lancer le script en passant par un shell
# subprocess.run(script, shell=True, check=True)

# Forcer les flux standard à passer directement
# subprocess.run(["/usr/bin/bash", "-c", script], check=True, stdout=None, stderr=None)
bash_path = shutil.which("bash.exe")
if bash_path is None:
    raise FileNotFoundError("bash.exe introuvable. Vérifiez que Git Bash est installé et dans le PATH.")

# output = subprocess.run([bash_path, "-c", script], check=True)

output = subprocess.run(
    [bash_path, "-c", script],
    check=True,
    capture_output=True,  # Capture stdout et stderr
    text=True  # Retourne les résultats en tant que chaîne de caractères
)




print(f"Output: {output.stdout}")
# subprocess.run(
#     [r"C:\Program Files\Git\bin\bash.exe", "-c", script], check=True
# )



# import pexpect

# script = """
# echo "Hello from Bash!"
# pwd
# """

# child = pexpect.spawn("bash", ["-c", script])
# child.logfile = sys.stdout  # Rediriger la sortie vers stdout
# child.expect(pexpect.EOF)  # Attendre la fin du script
