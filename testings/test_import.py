#!/usr/bin/env python3

import sys

module_name = 'tabulate'
if module_name in sys.modules:
    print(f"Le module '{module_name}' est déjà importé.")
else:
    print(f"Le module '{module_name}' n'est pas encore importé.")
